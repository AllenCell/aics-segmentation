from typing import List
from dataclasses import dataclass
from . import WorkflowStep

class WorkflowDefinition:
    """
    Definition of an aics-segmentation Workflow

    This class only defines the workflow (i.e. the workflow characteristics and steps)
    and is used either for building an executable Workflow object 
    or to access information about the Workflow without needing to execute it
    """

    name: str
    steps: List[WorkflowStep]

    # TODO
    # JSON encoder instead ?
    @staticmethod
    def from_json(self, json):        
        pass


