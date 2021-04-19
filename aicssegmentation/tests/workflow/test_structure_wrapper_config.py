import pytest

from aicssegmentation.workflow.structure_wrapper_config import StructureWrapperConfig
from . import SUPPORTED_STRUCTURE_NAMES


class TestStructureWrapperConfig:
    def setup_method(self):
        self._structure_wrapper_config = StructureWrapperConfig()

    def test_get_available_workflows(self):
        workflows = self._structure_wrapper_config.get_available_workflows()
        assert workflows == SUPPORTED_STRUCTURE_NAMES

    def test_functions_json_mapping(self):
        # TODO
        pass

    def test_workflow_definition_json_mapping(self):
        # TODO
        pass

    def test_get_all_functions(self):
        functions = self._structure_wrapper_config.get_all_functions()

        assert functions is not None
        assert len(functions) > 0

    @pytest.mark.parametrize("name", [None, "", "  "])
    def test_get_workflow_definition_empty_name_fails(self, name):
        with pytest.raises(ValueError):
            workflow_def = self._structure_wrapper_config.get_workflow_definition(
                name
            )  # noqa F841

    def test_get_workflow_definition_unavailable_workflow_fails(self):
        with pytest.raises(ValueError):
            workflow_def = (
                self._structure_wrapper_config.get_workflow_definition(  # noqa F841
                    "unsupported workflow"
                )
            )

    @pytest.mark.parametrize("name", SUPPORTED_STRUCTURE_NAMES)
    def test_get_workflow_definition(self, name):
        workflow_def = self._structure_wrapper_config.get_workflow_definition(name)
        assert workflow_def is not None
        assert workflow_def.name == name
