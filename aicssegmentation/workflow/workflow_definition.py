import numpy as np

from aicsimageio import imread
from typing import List
from dataclasses import dataclass
from aicssegmentation.util.lazy import lazy_property
from aicssegmentation.util.directories import Directories
from .workflow_step import WorkflowStep

@dataclass
class WorkflowDefinitionFromFile:
    """
        Definition of an aics-segmentation Workflow

        This class only defines the workflow (i.e. the workflow characteristics and steps)
        and is used either for building an executable Workflow object
        or to access information about the Workflow without needing to execute it
        """


    name: str
    steps: List[WorkflowStep]
    from_file: bool

    def __init__(self, name: str, steps: List[WorkflowStep]):
        self.name = name
        self.steps = steps
        self.from_file = True



@dataclass
class WorkflowDefinition(WorkflowDefinitionFromFile):
    """
    Definition of an aics-segmentation Workflow

    This class only defines the workflow (i.e. the workflow characteristics and steps)
    and is used either for building an executable Workflow object
    or to access information about the Workflow without needing to execute it
    """

    def __init__(self, name: str, steps: List[WorkflowStep]):
        WorkflowDefinitionFromFile.__init__(self, name=name, steps=steps)
        # Regular WorkflowDefinitions are not from a file
        self.from_file = False

    @lazy_property
    def thumbnail_pre(self) -> np.ndarray:
        """
        The Pre-segmentation thumbnail related to this workflow, as a numpy array
        """
        return np.squeeze(imread(Directories.get_assets_dir() / f"thumbnails/{self.name.lower()}_pre.png"))

    @lazy_property
    def thumbnail_post(self) -> np.ndarray:
        """
        The Post-segmentation thumbnail related to this workflow, as a numpy array
        """
        return np.squeeze(imread(Directories.get_assets_dir() / f"thumbnails/{self.name.lower()}_post.png"))

    @lazy_property
    def diagram_image(self) -> np.ndarray:
        """
        Diagram / flow chart image for this workflow, as a numpy array
        """
        return np.squeeze(imread(Directories.get_assets_dir() / f"diagrams/{self.name.lower()}.png"))
