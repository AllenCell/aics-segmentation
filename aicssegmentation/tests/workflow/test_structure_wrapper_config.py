import pytest

from aicssegmentation.workflow.structure_wrapper_config import StructureWrapperConfig

class TestStructureWrapperConfig:

    def test_get_all_functions(self):
        functions = StructureWrapperConfig.get_all_functions()

        assert functions is not None
        assert len(functions) > 0
        # TODO test for real


    @pytest.mark.parametrize("name", [None, "", "  "])    
    def test_get_workflow_definition_empty_name_fails(self, name):
        with pytest.raises(ValueError):
            workflow_def = StructureWrapperConfig.get_workflow_definition(name)        

    def test_get_workflow_definition(self):
        workflow_def = StructureWrapperConfig.get_workflow_definition("sec61b")
        assert workflow_def is not None

    def test_all_workflows_definitions(self):
        pass
