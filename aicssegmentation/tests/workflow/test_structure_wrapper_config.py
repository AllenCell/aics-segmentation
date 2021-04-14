from aicssegmentation.workflow.structure_wrapper_config import StructureWrapperConfig

class TestStructureWrapperConfig:

    def test_get_all_functions(self):
        functions = StructureWrapperConfig.get_all_functions()

        assert functions is not None
        assert len(functions) > 0
        # TODO test for real
