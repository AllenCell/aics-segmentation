import importlib
import numpy as np
from typing import Dict, List, Any


class WorkflowStep:
    """
    A class that defines a step in an AICS-Segmentation workflow.
    """

    def __init__(self, step_config: Dict[str, str], widget_info: Dict[str, Any]):
        """
        Constructor for the workflow object

        Params:
            step_config (dict): dictionary object containing
                                information about this workflow step

        """
        self.name: str = step_config["name"]  # Name of the workflow step
        self.parent: List[int] = None
        if isinstance(step_config["parent"], int):
            # single parent
            self.parent = [
                step_config["parent"] - 1
            ]  # Index of parent in entire workflow
            # TODO: Better to change json to 0-indexed to avoid confusion
        else:
            # multiple parents
            self.parent = [i - 1 for i in step_config["parent"]]
        self.result: np.ndarray = (
            None  # Result of running this step, None if not executed
        )

        self.module_name = step_config["module"]
        module = importlib.import_module(self.module_name)

        self.function_name = step_config["function"]
        self.__function = getattr(module, self.function_name)

        self.__parameters: dict[str, Any] = None
        if "parameter" in step_config:
            self.__parameters = step_config["parameter"]

        # Until we can get the category key into every json file
        # TODO: Remove this once we have category defined in every json file
        self.category = None  # preprocessing, core, or postprocessing?
        try:
            self.category = step_config["category"]
        except KeyError:
            self.category = None

        self.widget_data = self.__get_widget_data_step(widget_info)

    def execute(self, image: List[np.ndarray]) -> np.ndarray:
        """
        Execute this workflow step on a given image and return the result.
        Also sets the result field to the resultant image.

        Params:
            image (np.ndarray): Image to perform this workflow step on,
                                generally parent image

        Returns:
            self.result (np.ndarray): Result of performing workflow step
                                        on the given image.
        """

        if self.__parameters:
            self.result: np.ndarray = self.__function(*image, **self.__parameters)
        else:
            try:
                # Most functions require unpacking the images
                self.result: np.ndarray = self.__function(*image)
            except (AttributeError, TypeError):
                # Some functions want it as a list
                self.result: np.ndarray = self.__function(image)
        return self.result

    def get_params(self) -> Dict[str, Any]:
        """
        Get the parameter names and its default values for this step.

        Params:
            none

        Returns:
            (Dict[str, Any]): map of parameter names to default values. Default values
                could be a list, str, or int.
        """
        return self.__parameters

    def __get_widget_data_step(self, widget_info: Dict[str, Any]) -> Dict[str, Any]:
        for k, v in widget_info.items():
            if v["module"] == self.module_name:
                if v["function"] == self.function_name:
                    return {k: v}
        raise KeyError("There is no information about the widget for "
                       "\nmodule: {}\nfunction {}".format(self.module_name, self.function_name))

