from typing import Dict, List
from .segmenter_function import SegmenterFunction, FunctionParameter
from . import WorkflowDefinition

class ConfigurationException(Exception):
    """
    TODO    
    """
    def __init__(msg: str):
        super().__init__(msg)

def all_functions_decoder(obj: Dict) -> List[SegmenterFunction]:
    """
    Decode Functions config (all_functions.json)
    """    
    pass

def workflow_decoder(obj: Dict) -> WorkflowDefinition:
    """
    Decode Workflow config (conf_xxx.json)
    """
    pass