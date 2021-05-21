import numpy as np

from aicssegmentation.workflow.workflow import Workflow
from aicssegmentation.workflow.structure_wrapper_config import StructureWrapperConfig
from skimage import data
from aicsimageio.writers import writer
from pathlib import Path


class TestWorkflow:
    def setup_method(self):
        self._fake_image = np.asarray(data.astronaut())
        definition = StructureWrapperConfig().get_workflow_definition("sec61b")  # TODO use mock workflow
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
        #set up base folder
        test_base = testing_directory.joinpath("test")
        test_base.mkdir(parents=True, exist_ok=True)
        files = [f for f in testing_directory.glob("**/*") if f.is_file]
        # Currently will save files in same format as they are in the input path
        for f in files:
            f.unlink()

        #set up results folder
        test_results = testing_directory.joinpath("test_results")
        test_results.mkdir(parents=True, exist_ok=True)
        files = [f for f in test_results.glob("**/*") if f.is_file]
        # Currently will save files in same format as they are in the input path
        for f in files:
            f.unlink()



