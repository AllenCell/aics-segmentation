import numpy as np

from typing import List, Union
from .workflow import Workflow
from .workflow_definition import WorkflowDefinition
from .workflow_config import WorkflowConfig
from pathlib import Path
import json
from json import JSONDecodeError


class WorkflowEngine:
    """
    aicssegmentation workflow engine
    Use this class to access and execute aicssegmentation structure workflows
    """

    def __init__(self, workflow_config: WorkflowConfig = None):
        self._workflow_config = workflow_config or WorkflowConfig()
        self._workflow_definitions = self._load_workflow_definitions()

    @property
    def workflow_definitions(self) -> List[WorkflowDefinition]:
        """
        List of all workflow definitions
        """
        return self._workflow_definitions

    def get_executable_workflow(self, workflow_name: str, input_image: np.ndarray) -> Workflow:
        """
        Get an executable workflow object

        inputs:
            workflow_name (str): Name of the workflow to load
            input_image (ndarray): input image for the workflow to execute on
        """
        if input_image is None:
            raise ValueError("input_image")

        definition = next(filter(lambda d: d.name == workflow_name, self._workflow_definitions), None)
        if definition is None:
            raise ValueError(
                f"No available workflow definition found for {workflow_name}. Specify a valid workflow name."
            )

        return Workflow(definition, input_image)

    def get_executable_workflow_from_config_file(self, file_path: Union[str, Path], input_image: np.ndarray) -> Workflow:
        """
        Get an executable workflow object from a configuration file

        inputs:
            file_path (str|Path): Path to the workflow configuration file
            input_image (ndarray): input image for the workflow to execute on
        """                            
        if input_image is None:
            raise ValueError("input_image")
        if isinstance(file_path, str):
            norm_path = Path(file_path)
        elif isinstance(file_path, Path):
            norm_path = file_path
        else:
            raise ValueError("file_path")
        
        definition = self._workflow_config.get_workflow_definition_from_config_file(norm_path)
        return Workflow(definition, input_image)

    def _load_workflow_definitions(self) -> List[WorkflowDefinition]:
        definitions = list()
        available_workflows = self._workflow_config.get_available_workflows()
        for name in available_workflows:
            definitions.append(self._workflow_config.get_workflow_definition(name))
        return definitions
