import pytest

from aicssegmentation.workflow.workflow_config import WorkflowConfig
from aicssegmentation.util.directories import Directories
from aicssegmentation.workflow.workflow_definition import WorkflowDefinition, PrebuiltWorkflowDefinition
from . import SUPPORTED_STRUCTURE_NAMES


class TestStructureWrapperConfig:
    def setup_method(self):
        self._workflow_config = WorkflowConfig()

    def test_get_available_workflows(self):
        workflows = self._workflow_config.get_available_workflows()
        assert workflows == SUPPORTED_STRUCTURE_NAMES

    def test_get_all_functions(self):
        functions = self._workflow_config.get_all_functions()

        assert functions is not None
        assert len(functions) > 0

    @pytest.mark.parametrize("name", [None, "", "  "])
    def test_get_workflow_definition_empty_name_fails(self, name):
        with pytest.raises(ValueError):
            workflow_def = self._workflow_config.get_workflow_definition(name)

    def test_get_workflow_definition_unavailable_workflow_fails(self):
        with pytest.raises(ValueError):
            workflow_def = self._workflow_config.get_workflow_definition("unsupported workflow")

    @pytest.mark.parametrize("name", SUPPORTED_STRUCTURE_NAMES)
    def test_get_workflow_definition(self, name):
        workflow_def = self._workflow_config.get_workflow_definition(name)
        assert isinstance(workflow_def, PrebuiltWorkflowDefinition)
        assert workflow_def.name == name

    def test_get_workflow_definition_from_config_file(self):
        path = Directories.get_structure_config_dir() / "conf_actb.json" 
        workflow_def = self._workflow_config.get_workflow_definition_from_config_file(path)
        assert isinstance(workflow_def, WorkflowDefinition)
        assert workflow_def.name == "conf_actb.json"        
