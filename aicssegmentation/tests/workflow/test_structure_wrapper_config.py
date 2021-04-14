import pytest

from aicssegmentation.workflow.structure_wrapper_config import StructureWrapperConfig

ALL_STRUCTURE_NAMES = [
    "actb",
    "actn1",
    "atp2a2",
    "cetn2",
    "ctnnb1",
    "dsp",
    "fbl",
    "gja1",
    "h2b_interphase",
    "lamp1",
    "lmnb1_interphase",
    "lmnb1_mitotic",
    "myh10",
    "npm1",        
    "nup153",
    "pxn",
    "rab5a",
    "sec61b",    
    "slc25a17",
    "smc1a",
    "son",
    "st6gal1",
    "tjp1",
    "tomm20",
    "tuba1b"    
]

class TestStructureWrapperConfig:

    def test_functions_json_mapping(self):
        # TODO
        pass

    def test_workflow_definition_json_mapping(self):
        # TODO
        pass

    def test_get_all_functions(self):
        functions = StructureWrapperConfig.get_all_functions()

        assert functions is not None
        assert len(functions) > 0        

    @pytest.mark.parametrize("name", [None, "", "  "])    
    def test_get_workflow_definition_empty_name_fails(self, name):
        with pytest.raises(ValueError):
            workflow_def = StructureWrapperConfig.get_workflow_definition(name)        

    @pytest.mark.parametrize("name", ALL_STRUCTURE_NAMES)
    def test_get_workflow_definition(self, name):
        workflow_def = StructureWrapperConfig.get_workflow_definition(name)
        assert workflow_def is not None
        assert workflow_def.name == name
