import json
import functools

from typing import Dict, List
from aicssegmentation.util.directories import Directories
from .segmenter_function import SegmenterFunction, FunctionParameter
from .workflow_definition import WorkflowDefinition

class ConfigurationException(Exception):
    """
    Raised when errors are encountered reading from Configuration files
    """
    pass


class StructureWrapperConfig:
    @classmethod
    def get_all_functions(cls) -> List[SegmenterFunction]:
        """
        Get the list of all available Functions from structure configuration
        """
        path = Directories.get_structure_config_dir() / "all_functions.json"

        try:            
            with open(path) as file:
                obj = json.load(file)
                return cls._all_functions_decoder(obj)
        except Exception as ex:
            raise ConfigurationException(f"Error reading json configuration from {path}") from ex

    @classmethod
    def _all_functions_decoder(cls, obj: Dict) -> List[SegmenterFunction]:
        """
        Decode Functions config (all_functions.json)
        """    
        def build_function_parameter(name: str, data: Dict):
            return FunctionParameter(name=name,
                                     widget_type=data["widget_type"],
                                     data_type=data["data_type"],
                                     min_value=data.get("min", None),
                                     max_value=data.get("max", None),
                                     increment=data.get("increment", None),
                                     options=data.get("options", None)
                                    )
        
        functions = list()
        for function_k, function_v in obj.items():
            function = SegmenterFunction(display_name=function_v["name"],
                                        function=function_v["python::function"],
                                        module=function_v["python::module"])

            if(function_v.get("parameters") is not None and len(function_v["parameters"]) > 0):
                params = dict()

                for param_k, param_v in function_v["parameters"].items():
                    param_name = param_k
                    params[param_name] = list()
                    # TODO refactor
                    if type(param_v) == dict:                                            
                        params[param_name].append(build_function_parameter(param_name, param_v))                        
                    elif type(param_v) == list: 
                        for item in param_v:                                                   
                            params[param_name].append(build_function_parameter(param_name, item) )
                
                function.parameters = params

            functions.append(function)

        return functions
            

    @classmethod
    def _workflow_decoder(cls, obj: Dict) -> WorkflowDefinition:
        """
        Decode Workflow config (conf_{structure}.json)
        """
        pass
