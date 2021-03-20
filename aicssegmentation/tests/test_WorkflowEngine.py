import pytest
from unittest.mock import MagicMock, create_autospec
import numpy as np
from aicssegmentation.structure_wrapper.WorkflowEngine import WorkflowEngine
from skimage import data


class TestWorkflowEngine:
    def setup_method(self):
        caller = getattr(data, "astronaut")
        image = caller()
        self.fake_image = np.asarray(image)
        self.engine = WorkflowEngine("sec61b", self.fake_image)

    def test_get_next_step(self):
        assert self.engine.get_next_step().name == "Intensity Normalization"
        self.engine.execute_next()
        assert self.engine.get_next_step().name == "Edge Preserving Smoothing"

    def test_execute_next(self):
        assert self.engine.next_step == 0
        assert self.engine.steps[0].result is None
        self.engine.execute_next()
        assert self.engine.next_step == 1
        assert self.engine.steps[0].result is not None
        self.engine.execute_next()
        assert self.engine.next_step == 2
        assert self.engine.steps[1].result is not None

    def test_get_result(self):
        assert self.engine.get_result(0) is None
        self.engine.execute_next()
        assert isinstance(self.engine.get_result(0), np.ndarray)
        assert self.engine.get_result(1) is None

    def test_get_most_recent_result(self):
        assert np.array_equal(self.fake_image, self.engine.get_most_recent_result())

    def test_execute_all(self):
        self.engine.execute_all()
        assert self.engine.next_step == 4

    def test_is_done(self):
        self.engine.execute_all()
        assert self.engine.is_done()
