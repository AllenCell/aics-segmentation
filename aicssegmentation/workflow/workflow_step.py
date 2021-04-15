import importlib
import numpy as np

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any
from .segmenter_function import SegmenterFunction


class WorkflowStepCategory(Enum):
    PRE_PROCESSING = "preprocessing"
    CORE = "core"
    POST_PROCESSING = "postprocessing"

    @staticmethod
    def from_str(value: str):
        if value is not None:
            value = value.lower()
        if value == WorkflowStepCategory.PRE_PROCESSING.value:
            return WorkflowStepCategory.PRE_PROCESSING
        if value == WorkflowStepCategory.CORE.value:
            return WorkflowStepCategory.CORE
        if value == WorkflowStepCategory.POST_PROCESSING.value:
            return WorkflowStepCategory.POST_PROCESSING            
        raise NotImplementedError()
            

@dataclass
class WorkflowStep:
    """
    Represents a single step in an aicssegmentation Workflow
    """

    category: WorkflowStepCategory
    function: SegmenterFunction
    step_number: int    
    parent: List[int]
    parameter_defaults: Dict[str, List] = None
    
    @property
    def name(self):        
        return self.function.display_name

    def execute(self, image: List[np.ndarray], parameters: Dict[str, Any] = None) -> np.ndarray:
        """
        Execute this workflow step on a given image and return the result.
        Also sets the result field to the resultant image.

        Params:
            image (List[np.ndarray]): List of image inputs to perform this workflow step on,
                                      generally parent image
            parameters (Dict): Dictionary of parameters to pass to the
                                underlying function

        Returns:
            self.result (np.ndarray): Result of performing workflow step
                                        on the given image.
        """        
        
        py_module = importlib.import_module(self.function.module)        
        py_function = getattr(py_module, self.function.function)

        if parameters is not None:
            return py_function(*image, **parameters)
        else:
            try:
                # Most functions require unpacking the images
                return py_function(*image)
            except (KeyError, TypeError):
                # Some functions want it as a list
                return py_function(image)
