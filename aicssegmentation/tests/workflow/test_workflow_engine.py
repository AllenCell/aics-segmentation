from aicssegmentation.workflow.workflow import Workflow
import pytest
import numpy as np

from unittest.mock import MagicMock, create_autospec
from aicssegmentation.workflow.structure_wrapper_config import StructureWrapperConfig
from aicssegmentation.workflow.workflow_engine import WorkflowEngine, WorkflowDefinition


class TestWorkflowEngine:  
    expected_workflow_names = ["sec61b", "actn1", "test123"]
    expected_workflow_definitions = [
        WorkflowDefinition(name="sec61b", steps=list()),
        WorkflowDefinition(name="actn1", steps=list()),
        WorkflowDefinition(name="test123", steps=list())
    ]

    def setup_method(self):
        self._mock_structure_config: MagicMock = create_autospec(StructureWrapperConfig)
        self._mock_structure_config.get_available_workflows.return_value = self.expected_workflow_names
        self._mock_structure_config.get_workflow_definition.side_effect = self.expected_workflow_definitions
        self._workflow_engine = WorkflowEngine(self._mock_structure_config)
    
    def test_workflow_definitions(self):
        assert self._workflow_engine.workflow_definitions == self.expected_workflow_definitions

    def test_get_executable_workflow_null_image_fails(self):
        with pytest.raises(ValueError):
            self._workflow_engine.get_executable_workflow("sec61b", None)

    def test_get_executable_workflow_unsupported_workflow_fails(self):
        with pytest.raises(ValueError):
            self._workflow_engine.get_executable_workflow("unsupported", np.ones((1,1,1)))

    @pytest.mark.parametrize("workflow_name", ["sec61b", "actn1", "test123"])
    def test_get_executable_workflow(self, workflow_name):
        workflow = self._workflow_engine.get_executable_workflow(workflow_name, np.ones((1,1,1)))        
        assert isinstance(workflow, Workflow)
        assert workflow.workflow_definition.name == workflow_name
        