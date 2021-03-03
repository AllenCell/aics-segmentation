from aicssegmentation.structure_wrapper_config.structure_config_utils import load_workflow_config, parse_config_to_objects
import numpy as np
from aicssegmentation.structure_wrapper.WorkflowStep import WorkflowStep


class WorkflowEngine:
    """
    A class to define a whole aics-segmentation workflow
    """
    def __init__(self, workflow_name: str, image: np.ndarray):
        """
        Constructor for the WorkflowEngine object

        Params:
            workflow_name (str): dictionary object containing information about this workflow step
            image (np.ndarray):  image to perform workflow on
        """
        self.workflow_name: str = workflow_name   # Workflow name
        self.steps: list = self.__get_steps()        # List of WorkflowSteps for this workflow
        self.currentStep: int = 0                 # Next step to execute
        self.starting_image: np.ndarray = image          # Initial image

    def __get_steps(self) -> list:
        """
        Get a list of WorkflowStep objects to perform on the starting image.

        Params:
            none

        Returns:
            (list(WorkflowStep)): List of workflow step objects
       """
        # TODO: in order for parent fucntionality to work correctly, we should sort these in the list by parent index
        return parse_config_to_objects(load_workflow_config(self.workflow_name))

    def get_next_step(self) -> WorkflowStep:
        """
        Get the next step to be performed

        Params:
            none

        Returns:
            (WorkflowStep): next WorkflowStep object to perform on image
       """
        return self.steps[self.currentStep]

    def execute_next(self) -> np.ndarray:
        """
        Execute the next workflow step.

        Params:
            none

        Returns:
            result (np.ndarray): resultant image from running the next workflow step
       """
        # Pick which image to perform the workflow step on
        image: np.ndarray = None
        if self.currentStep == 0:
            # First image, so use the starting image for the next workflow step
            image = self.starting_image
        elif self.isDone():
            # No more workflow steps to perform
            # TODO: what to do if done with workflow but execute_next is prompted?
            # printing message for now
            print("No steps left to run")
        else:
            # First step has been run, so run next workflow step with the result of its parent
            image = self.get_result(self.get_next_step().parent)

        result: np.ndarray = self.get_next_step().execute(image)

        # Only increment after running step
        self.currentStep = self.currentStep + 1
        return result


    def get_result(self, step_index: int) -> np.ndarray:
        """
        Get the result image for a workflow step.
        You must call execute() on the workflow step in order to produce a result first before calling this function.

        Params:
            step_index (int): index of the WorkflowStep in the workflowengine to get the result image of.

        Returns:
            self.image (np.ndarray): Result of performing workflow step on the given image
                                     None if step has not been executed yet.
       """
        if step_index > self.currentStep:
            return None # returns None if the WorkflowStep has not been executed.
        else:
            return self.steps[step_index].result

    def get_most_recent_result(self) -> np.ndarray:
        """
        Get the result from the last executed WorkflowStep.

        Params:
           none

        Returns:
            (np.ndarray): Result of the last executed WorkflowStep, returns the starting image if no Workflowsteps have
                            been run.
       """
        if self.currentStep == 0:
            return self.starting_image
        else:
            return self.get_result(self.currentStep - 1)

    def execute_all(self) -> np.ndarray:
        """
        Execute all the remaining WorkflowSteps in the WorkflowEngine.

        Params:
            none

        Returns:
            (np.ndarray): Result of the final WorkflowStep.
       """
        while not self.isDone():
            self.execute_next()
        return self.get_most_recent_result()

    def isDone(self) -> bool:
        """
        Check if all WorkflowSteps have been executed.

        Params:
            none

        Returns:
            (bool): True if all WorkflowSteps have been executed, False if not
       """
        return self.currentStep >= len(self.steps)

