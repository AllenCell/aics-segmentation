import json

from typing import Dict, List
from aicssegmentation.util.directories import Directories
from .segmenter_function import SegmenterFunction, FunctionParameter, WidgetType
from .workflow_definition import WorkflowDefinition
from .workflow_step import WorkflowStep, WorkflowStepCategory


class ConfigurationException(Exception):
    """
    Raised when errors are encountered reading from Configuration files
    """
    pass


class StructureWrapperConfig:
    _all_functions = None
    _available_workflow_names = None

    @classmethod
    def get_available_workflows(cls) -> List[str]:
        """
        Get the list of all workflows available through configuration 
        """
        if cls._available_workflow_names is None:
            json_list = sorted(Directories.get_structure_config_dir().glob("conf_*.json"))
            cls._available_workflow_names = [p.stem[5:] for p in json_list]

        return cls._available_workflow_names

    @classmethod
    def get_all_functions(cls) -> List[SegmenterFunction]:
        """
        Get the list of all available Functions from configuration
        """
        if cls._all_functions is None:
            path = Directories.get_structure_config_dir() / "all_functions.json"

            try:            
                with open(path) as file:
                    obj = json.load(file)
                    cls._all_functions = cls._all_functions_decoder(obj)
            except Exception as ex:
                raise ConfigurationException(f"Error reading json configuration from {path}") from ex
        
        return cls._all_functions
    
    @classmethod
    def get_workflow_definition(cls, workflow_name: str):
        """
        Get a WorkflowDefinition for the given workflow from the corresponding json structure config
        """
        if workflow_name is None or len(workflow_name.strip()) == 0:
            raise ValueError("workflow_name cannot be empty")

        if workflow_name not in cls.get_available_workflows():
            raise ValueError(f"No workflow configuration available for {workflow_name}")

        path = Directories.get_structure_config_dir() / f"conf_{workflow_name}.json"

        try:            
            with open(path) as file:
                obj = json.load(file)
                return cls._workflow_decoder(obj, workflow_name)
        except Exception as ex:
            raise ConfigurationException(f"Error reading json configuration from {path}") from ex        

    @classmethod
    def _all_functions_decoder(cls, obj: Dict) -> List[SegmenterFunction]:
        """
        Decode Functions config (all_functions.json)
        """    
        def build_function_parameter(name: str, data: Dict):
            return FunctionParameter(name=name,
                                     widget_type=WidgetType.from_str(data["widget_type"]),
                                     data_type=data["data_type"],
                                     min_value=data.get("min", None),
                                     max_value=data.get("max", None),
                                     increment=data.get("increment", None),
                                     options=data.get("options", None)
                                    )
        
        functions = list()
        for function_k, function_v in obj.items():
            function = SegmenterFunction(name = function_k,
                                         display_name=function_v["name"],
                                         function=function_v["python::function"],
                                         module=function_v["python::module"])

            if(function_v.get("parameters") is not None and len(function_v["parameters"]) > 0):
                params = dict()

                for param_k, param_v in function_v["parameters"].items():
                    param_name = param_k
                    params[param_name] = list()
                    
                    if isinstance(param_v, dict):  
                        params[param_name].append(build_function_parameter(param_name, param_v))                        
                    elif isinstance(param_v, list):
                        for item in param_v:                                                   
                            params[param_name].append(build_function_parameter(param_name, item) )
                
                function.parameters = params

            functions.append(function)

        return functions
            

    @classmethod
    def _workflow_decoder(cls, obj: Dict, workflow_name: str) -> WorkflowDefinition:
        """
        Decode Workflow config (conf_{workflow_name}.json)
        """
        functions = cls.get_all_functions()
        steps = list()

        for step_k, step_v in obj.items():
            step_number = int(step_k)
            function = next(filter(lambda f: f.name == step_v["function"], functions))
            
            if isinstance(step_v["parent"], list): #
                parent = step_v["parent"]
            else:
                parent = [step_v["parent"]]


            step = WorkflowStep(category=WorkflowStepCategory.from_str(step_v["category"]),
                                function=function, 
                                step_number=step_number, 
                                parent=parent)

            if(step_v.get("parameter_defaults") is not None and len(step_v["parameter_defaults"]) > 0):
                param_defaults = dict()

                for param_k, param_v in step_v["parameter_defaults"].items():
                    param_name = param_k                    
                    param_defaults[param_name] = param_v                    
                
                step.parameter_defaults = param_defaults
            
            steps.append(step)
        
        return WorkflowDefinition(name=workflow_name, steps=steps)

