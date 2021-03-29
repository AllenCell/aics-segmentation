import numpy as np
from aicssegmentation.structure_wrapper.WorkflowEngine import WorkflowStep
from skimage import data
import pytest


class TestWorkflowStep:
    def setup_method(self):
        caller = getattr(data, "astronaut")
        image = caller()
        self.fake_image = np.asarray(image)
        self.test_dict = dict()
        self.step = None

    def test_default_exec(self):
        self.test_dict["name"] = "intensity_normalization"
        self.test_dict["module"] = "aicssegmentation.core.pre_processing_utils"
        self.test_dict["function"] = "intensity_normalization"
        self.test_dict["parent"] = 0
        self.test_dict["parameter"] = {"scaling_param": [3, 15]}
        self.step = WorkflowStep(self.test_dict)
        # default execution with parameters
        assert self.step.result is None
        self.step.execute([self.fake_image])
        assert isinstance(self.step.result, np.ndarray)

    def test_exec_no_param(self):
        del self.test_dict["parameter"]
        self.test_dict["name"] = "Edge Preserving Smoothing"
        self.test_dict["module"] = "aicssegmentation.core.pre_processing_utils"
        self.test_dict["function"] = "edge_preserving_smoothing_3d"
        self.test_dict["parent"] = 1
        self.step = WorkflowStep(self.test_dict)
        assert self.step.result is None
        self.step.execute([self.fake_image])
        assert isinstance(self.step.result, np.ndarray)

    def test_exec_multi_image(self):
        self.test_dict["name"] = "Merge Segmentation"
        self.test_dict["module"] = "aicssegmentation.core.utils"
        self.test_dict["function"] = "segmentation_union"
        self.test_dict["parent"] = [1, 2]
        self.step = WorkflowStep(self.test_dict)
        assert self.step.result is None
        with pytest.raises(Exception):
            self.step.execute([self.fake_image, self.fake_image])
        assert isinstance(self.step.result, np.ndarray)
