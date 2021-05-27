import numpy as np

from unittest.mock import MagicMock, patch
from aicsimageio.writers import OmeTiffWriter
from pathlib import Path
from aicsimageio import AICSImage
from numpy import random
from aicssegmentation.workflow.batch_workflow import BatchWorkflow
from aicssegmentation.workflow.workflow_config import WorkflowConfig


class TestBatchWorkflow:
    def setup_method(self):
        testing_directory = Path(__file__).parent.joinpath("resources")
        # set up base folder
        self.test_base = testing_directory.joinpath("test")
        self.test_base.mkdir(parents=True, exist_ok=True)
        files = [f for f in self.test_base.glob("**/*") if f.is_file]
        # Currently will save files in same format as they are in the input path
        for f in files:
            f.unlink()

        # set up results folder
        self.test_results = testing_directory.joinpath("test_results")
        self.test_results.mkdir(parents=True, exist_ok=True)
        files = [f for f in self.test_results.glob("**/*") if f.is_file]
        # Currently will save files in same format as they are in the input path
        for f in files:
            f.unlink()

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

    @patch("aicssegmentation.workflow.batch_workflow.Workflow.execute_all")
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
