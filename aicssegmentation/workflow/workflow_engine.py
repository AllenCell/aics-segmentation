import numpy as np

from typing import List
from .workflow import Workflow
from .workflow_definition import WorkflowDefinition
from .structure_wrapper_config import StructureWrapperConfig


class WorkflowEngine:
    """
    aicssegmentation workflow engine
    Use this class to access and execute aicssegmentation structure workflows
    """

    def __init__(self, structure_config: StructureWrapperConfig = None):
        self._structure_config = structure_config or StructureWrapperConfig()
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
            image (ndarray): input image for the workflow to execute on
        """
        if input_image is None:
            raise ValueError("input_image")

        definition = next(filter(lambda d: d.name == workflow_name, self._workflow_definitions), None)
        if definition is None:
            raise ValueError(
                f"No available workflow definition found for {workflow_name}. Specify a valid workflow name."
            )

        return Workflow(definition, input_image)

    def _load_workflow_definitions(self) -> List[WorkflowDefinition]:
        definitions = list()
        available_workflows = self._structure_config.get_available_workflows()
        for name in available_workflows:
            definitions.append(self._structure_config.get_workflow_definition(name))
        return definitions
