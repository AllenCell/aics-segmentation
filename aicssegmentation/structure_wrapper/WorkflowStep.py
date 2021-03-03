import importlib
import numpy as np

class WorkflowStep:
    """
    A class that defines a step in an AICS-Segmentation workflow.
    """
    def __init__(self, step_config: dict):
        """
        Constructor for the workflow object

        Params:
            step_config (dict): dictionary object containing information about this workflow step
        """
        self.name: str = step_config["name"]         # Name of the workflow step
        self.parent: int = step_config["parent"] - 1 # Index of parent in entire workflow #TODO: Better to change jason to 0-indexed to avoid confusion
        self.result: np.ndarray = None               # Result of running this step, None if not executed

        module = importlib.import_module(step_config["module"])
        self.__function = getattr(module, step_config["function"])
        self.__parameters: dict = None
        if "parameter" in step_config:
            self.__parameters = step_config["parameter"]

    def execute(self, image: np.ndarray) -> np.ndarray:
        """
        Execute this workflow step on a given image and return the result.
        Also sets the result field to the resultant image.

        Params:
            image (np.ndarray): Image to perform this workflow step on, generally parent image

        Returns:
            self.result (np.ndarray): Result of performing workflow step on the given image.
       """
        if self.__parameters:
            self.result: np.ndarray = self.__function(image, **self.__parameters)
        else:
            self.result: np.ndarray = self.__function(image)
        return self.result
