from typing import Dict, List
from dataclasses import dataclass
from .workflow_step import WorkflowStep

@dataclass
class WorkflowDefinition:
    """
    Definition of an aics-segmentation Workflow

    This class only defines the workflow (i.e. the workflow characteristics and steps)
    and is used either for building an executable Workflow object 
    or to access information about the Workflow without needing to execute it
    """

    name: str
    steps: List[WorkflowStep]        

    # TODO get thumbnails


