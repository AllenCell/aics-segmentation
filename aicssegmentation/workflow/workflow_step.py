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

    def execute(self, input_images: List[np.ndarray], parameters: Dict[str, Any] = None) -> np.ndarray:
        """
        Execute this workflow step on the given input image and return the result.

        Params:
            input_images (List[np.ndarray]): List of image inputs to perform this
                    workflow step on, generally parent image
            parameters (Dict): Dictionary of parameters to pass to the
                                underlying function

        Returns:
            self.result (np.ndarray): Result of performing workflow step
                                        on the given image.
        """
        if not isinstance(input_images, list):
            raise ValueError("input_images must be a list")

        py_module = importlib.import_module(self.function.module)
        py_function = getattr(py_module, self.function.function)

        try:
            # Most functions require unpacking the images
            if parameters is not None:
                return py_function(*input_images, **parameters)

            return py_function(*input_images)
        except TypeError:
            # Some functions want it as a list
            if parameters is not None:
                return py_function(input_images, **parameters)
            return py_function(input_images)
