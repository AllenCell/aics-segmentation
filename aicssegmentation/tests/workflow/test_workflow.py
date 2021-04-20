from aicssegmentation.tests.workflow import SUPPORTED_STRUCTURE_NAMES
import pytest
import numpy as np
from aicssegmentation.workflow.workflow import Workflow
from aicssegmentation.workflow.structure_wrapper_config import StructureWrapperConfig
from skimage import data


class TestWorkflow:
    def setup_method(self):
        self._fake_image = np.asarray(data.astronaut())
        definition = StructureWrapperConfig().get_workflow_definition("sec61b")
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

    # TODO eventually turn into a proper end to end test of all configurable workflows
    #      currently this just makes sure that all workflows are properly loaded and
    #      can be executed through the engine. However, we use a fake 2D image so this is
    #      not an actual end to end test of the workflows
    #      Note: workflows are currently properly tested in tests/test_structures.py
    @pytest.mark.parametrize("name", SUPPORTED_STRUCTURE_NAMES)
    def test_execute_all_workflows(self, name):
        definition = StructureWrapperConfig().get_workflow_definition(name)
        workflow = Workflow(definition, self._fake_image)
        workflow.execute_all()
        assert workflow.get_next_step() is None
        assert workflow.is_done()
