from typing import List
from .workflow import Workflow
from .workflow_definition import WorkflowDefinition
from .structure_wrapper_config import StructureWrapperConfig

class WorkflowEngine:
    def __init__(self):
        self._workflow_definitions = self._load_workflow_definitions()
        
    @property
    def workflow_definitions(self) -> List[WorkflowDefinition]:
        """
        List of all workflow definitions
        """
        return self._workflow_definitions

    def get_executable_workflow(self, workflow_name: str) -> Workflow:
        """
        Get an executable workflow object

        inputs:
            workflow_name: Name of the workflow to load
        """
        # TODO implement
        raise NotImplementedError()

    def _load_workflow_definitions(self):
        definitions = list()
        available_workflows = StructureWrapperConfig.get_available_workflows()
        for name in available_workflows:
            definitions.append(StructureWrapperConfig.get_workflow_definition(name))
        return definitions
