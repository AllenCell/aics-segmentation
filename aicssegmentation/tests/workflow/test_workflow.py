import numpy as np

from aicssegmentation.workflow.workflow import Workflow, BatchWorkflow
from aicssegmentation.workflow.workflow_config import WorkflowConfig

from skimage import data
from aicsimageio.writers import OmeTiffWriter
from pathlib import Path
from aicsimageio import AICSImage
from numpy import random

from unittest.mock import MagicMock, patch


class TestWorkflow:
    def setup_method(self):
        self._fake_image = np.asarray(data.astronaut())
        definition = WorkflowConfig().get_workflow_definition("sec61b")  # TODO use mock workflow
        self._workflow = Workflow(definition, self._fake_image)

    def test_step_by_step_workflow_sec61b(self):
        assert self._workflow.get_result(0) is None
        assert np.array_equal(self._fake_image, self._workflow.get_most_recent_result())
        assert self._workflow.get_next_step().step_number == 1

        image1 = self._workflow.execute_next()
        assert self._workflow.get_next_step().step_number == 2
        assert np.array_equal(image1, self._workflow.get_most_recent_result())
        assert np.array_equal(image1, self._workflow.get_result(0))

        image2 = self._workflow.execute_next()
        assert self._workflow.get_next_step().step_number == 3
        assert np.array_equal(image2, self._workflow.get_most_recent_result())
        assert np.array_equal(image2, self._workflow.get_result(1))

        image3 = self._workflow.execute_next()
        assert self._workflow.get_next_step().step_number == 4
        assert np.array_equal(image3, self._workflow.get_most_recent_result())
        assert np.array_equal(image3, self._workflow.get_result(2))

        image4 = self._workflow.execute_next()
        assert self._workflow.get_next_step() is None
        assert np.array_equal(image4, self._workflow.get_most_recent_result())
        assert np.array_equal(image4, self._workflow.get_result(3))

        assert self._workflow.is_done()

    def test_execute_all_sec61b(self):
        self._workflow.execute_all()
        assert self._workflow.get_next_step() is None
        assert self._workflow.is_done()


class TestBatchWorkflow:
    def setup_method(self):
        testing_directory = Path(__file__).parent.joinpath("resources")
        # set up base folder
        self.test_base = testing_directory.joinpath("test")
        self.test_base.mkdir(parents=True, exist_ok=True)
        files = [f for f in self.test_base.glob("**/*") if f.is_file]
        # Currently will save files in same format as they are in the input path
        for f in files:
            f.unlink(missing_ok=True)

        # set up results folder
        self.test_results = testing_directory.joinpath("test_results")
        self.test_results.mkdir(parents=True, exist_ok=True)
        files = [f for f in self.test_results.glob("**/*") if f.is_file]
        # Currently will save files in same format as they are in the input path
        for f in files:
            f.unlink(missing_ok=True)

        # to save a test image
        three_d_image = np.zeros([2, 2, 2])
        with OmeTiffWriter(self.test_base.joinpath("test.tiff"), overwrite_file=True) as w:
            w.save(data=three_d_image, dimension_order="ZYX")
        self.valid_image = self.test_base.joinpath("test.tiff")

        definition = WorkflowConfig().get_workflow_definition("sec61b")
        self.batch_workflow = BatchWorkflow(definition, self.test_base, self.test_results, channel_index=0)

    def test_is_valid_image(self):

        self.invalid_paths = [
            self.test_base.joinpath("non_existant_image.tiff"),
            self.test_base.joinpath("bad_extension.abc"),
        ]
        for path in self.invalid_paths:
            assert not self.batch_workflow.is_valid_image(path)

        assert self.batch_workflow.is_valid_image(self.test_base / "test.tiff")

    def test_format_image_to_3d(self):

        three_d_image = AICSImage(random.random((2, 3, 4)), known_dims="ZYX")
        assert len(self.batch_workflow.format_image_to_3d(three_d_image).shape) == 3

    def test_convert_bool_to_uint8(self):
        array_to_test = np.zeros((5))
        array_to_test.data[0] = 1
        array_to_test.data[4] = 1
        converted = self.batch_workflow.convert_bool_to_uint8(array_to_test)
        assert np.array_equal(converted, [255, 0, 0, 0, 255])

    @patch("aicssegmentation.workflow.workflow.Workflow.execute_all")
    def test_process_all(self, mock_workflow_execute_all):
        mock_workflow_execute_all.return_value = np.zeros([2, 2, 2])
        self.batch_workflow.process_all()
        assert self.test_results.exists()
        assert self.test_results.joinpath("log.txt").exists()
        self.valid_image.unlink()
        self.test_base.rmdir()
        self.test_results.joinpath("test.tiff").unlink()
        self.test_results.joinpath("log.txt").unlink()
        self.test_results.rmdir()
