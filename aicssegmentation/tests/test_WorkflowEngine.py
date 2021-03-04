import pytest
from unittest.mock import MagicMock, create_autospec
import numpy as np
from aicssegmentation.structure_wrapper.WorkflowEngine import WorkflowEngine

class TestWorkflowEngine:
    def setup_method(self):
        self.fake_image = np.zeros([100,100])
        self.engine = WorkflowEngine("sec61b", self.fake_image)

    def test_get_next_step(self):
        assert self.engine.get_next_step().name == "Intensity Normalization"
        self.engine.execute_next()
        assert self.engine.get_next_step().name == "Edge Preserving Smoothing"
        self.engine = WorkflowEngine("sec61b", self.fake_image)

    def test_execute_next(self):
        assert self.engine.currentStep == 0
        assert self.engine.steps[0].result is None
        self.engine.execute_next()
        assert self.engine.currentStep == 1
        assert self.engine.steps[0].result is not None
        self.engine.execute_next()
        assert self.engine.currentStep == 2
        assert self.engine.steps[1].result is not None



