from typing import Any, Dict, List
import numpy as np
import logging
from aicsimageio import imread, AICSImage

from .workflow_step import WorkflowStep
from .workflow_definition import WorkflowDefinition, PrebuiltWorkflowDefinition

from pathlib import Path
from os import listdir

log = logging.getLogger(__name__)


class Workflow:
    """
    Represents an executable aics-segmentation workflow
    This class provides the functionality to run a workflow using an image input
    according to the steps defined in its WorkflowDefinition.
    """

    def __init__(self, workflow_definition: PrebuiltWorkflowDefinition, input_image: np.ndarray):
        if workflow_definition is None:
            raise ValueError("workflow_definition")
        if input_image is None:
            raise ValueError("image")
        self._definition: PrebuiltWorkflowDefinition = workflow_definition
        self._starting_image: np.ndarray = input_image
        self._next_step: int = 0  # Next step to execute
        self._results: List = list()  # Store step results

    @property
    def workflow_definition(self) -> PrebuiltWorkflowDefinition:
        return self._definition

    def reset(self):
        """
        Reset the workflow so it can be run again
        """
        self._next_step = 0
        self._results = list()

    def get_next_step(self) -> WorkflowStep:
        """
        Get the next step to be performed

        Params:
            none

        Returns:
            (WorkflowStep): next WorkflowStep object to perform on image
            None if all steps have already been executed
        """
        if self._next_step >= len(self._definition.steps):
            return None
        return self._definition.steps[self._next_step]

    def execute_next(self, parameters: Dict[str, Any] = None) -> np.ndarray:
        """
        Execute the next workflow step.

        Params:
            parameters: Optional dictionary of parameter inputs to use when executing the step
                        If parameters are not provided, the step's default parameters will be used

        Returns:
            result (np.ndarray): resultant image from running the
            next workflow step
        """
        log.info(f"Executing step #{self._next_step}")

        step = self.get_next_step()

        # Pick which image to perform the workflow step on
        image: np.ndarray = None

        if self._next_step == 0:
            # First image, so use the starting image for the next workflow step
            image = [self._starting_image]
        elif self.is_done():
            # No more workflow steps to perform
            # TODO: what to do if done with workflow
            #  but execute_next is prompted?
            # printing message for now
            log.info("No steps left to run")
        else:
            image = list()
            for i in step.parent:
                res = self.get_result(i - 1)  # parents are 1 indexed
                image.append(res)

        result: np.ndarray = self.get_next_step().execute(image, parameters or step.parameter_defaults)
        self._results.append(result)

        # Only increment after running step
        self._next_step += 1
        return result

    # TODO maybe change this to match the step number instead?
    #      Review when we implement rerunning single workflow steps
    def get_result(self, step_index: int) -> np.ndarray:
        """
        Get the result image for a workflow step.

        You must call execute() on the workflow step in order to
        produce a result first before calling this function.

        Params:
            step_index (int): index of the WorkflowStep in the
            workflowengine to get the result image of.

        Returns:
            self.image (np.ndarray): Result of performing workflow step
                                     on the given image
                                     None if step has not been executed yet.
        """
        if step_index < 0:
            return self._starting_image
        if step_index >= len(self._results):
            return None  # returns None if the WorkflowStep has not been executed.

        return self._results[step_index]

    def get_most_recent_result(self) -> np.ndarray:
        """
        Get the result from the last executed WorkflowStep.

        Params:
           none

        Returns:
            (np.ndarray): Result of the last executed WorkflowStep,
                            returns the starting image if no Workflowsteps have
                            been run.
        """
        if self._next_step == 0:
            return self._starting_image  # TODO does this behavior make sense? Return None instead?
        else:
            return self.get_result(self._next_step - 1)

    def execute_all(self) -> np.ndarray:
        """
        Execute all steps in the Workflow
        Note: default parameters will be used to execute the steps. To execute a step
              with user-provided parameters, use execute_next()

        Params:
            none

        Returns:
            (np.ndarray): Result of the final WorkflowStep.
        """
        self.reset()
        while not self.is_done():
            self.execute_next()
        return self.get_most_recent_result()

    def is_done(self) -> bool:
        """
        Check if all WorkflowSteps have been executed.

        Params:
            none

        Returns:
            (bool): True if all WorkflowSteps have been executed, False if not
        """
        return self._next_step >= len(self._definition.steps)


class BatchWorkflow:
    """
    Represents a batch of workflows to process.
    This class provides the functionality to run batches of workflows using multiple image inputs from a input directory
    according to the steps defined in its WorkflowDefinition.
    """

    def __init__(
        self, workflow_definition: WorkflowDefinition, input_dir: str, output_dir: str, channel_index: int = 0
    ):
        if workflow_definition is None:
            raise ValueError("workflow_definition")
        self._workflow_definition = workflow_definition

        self.input_path = Path(input_dir)
        if not self.input_path.exists():
            raise ValueError("The input directory does not exist")

        self.output_path = Path(output_dir)
        # Creating an the output directory at output_dir if it does not exist already
        if not self.output_path.exists():
            if self.output_path.parent.exists():
                self.output_path.mkdir(parents=True, exist_ok=True)
            else:
                raise ValueError(f"Output directory does not exist, and cannot be created at {self.output_path.parent}")

        self.files_count: int = 0
        self.failed_files: Dict[Path, str] = dict()
        self._channel_index = channel_index

    def is_valid_image(self, image_path: Path) -> bool:
        """
        Check if file at a given image_path is a valid image type we support (

        Params:
            image_path (Path): image to check

        Returns:
            (bool): True if all images are .tiff
        """
        if (
            image_path.suffix.lower() == ".tiff"
            or image_path.suffix.lower() == ".tif"
            or image_path.suffix.lower() == ".czi"
        ):
            return True
        else:
            return False

    def process_all(self):
        """
        Process all images in the input_dir with the workflow_definition used to set up the BatchWorkflow

        Params:
            none

        Returns:
            none
        """
        # Currently will save files in same format as they are in the input path
        for f in listdir(self.input_path):
            full_path = Path(self.input_path).joinpath(f)
            self.files_count += 1
            if self.is_valid_image(full_path):
                # read and format image in the way we expect
                image_from_path = imread(full_path).squeeze()
                if image_from_path.ndim > 4:
                    raise ValueError("Image is over 4 dims")
                if image_from_path.ndim == 4:
                    image_from_path = image_from_path[self._channel_index, :, :, :]
                try:
                    # Run workflow on image
                    workflow = Workflow(self._workflow_definition, image_from_path)
                    result = workflow.execute_all()
                except Exception as e:
                    # Handle failures during workflow execution/save
                    self.failed_files[full_path] = f"Failed during processing with error {e}"
            else:
                self.failed_files[full_path] = f"Unsupported image type {full_path.suffix}"
        self.write_log_file()

    def write_log_file(self):
        """
        Write a log file to the output folder.

        Params:
            image_path (Path): image to check

        Returns:
            (bool): True if all images are .tiff
        """
        if self.files_count == 0:
            raise RuntimeError("process_all has not been run yet, no logs to write.")

        with open(self.output_path.joinpath("log.txt"), "w") as f:
            files_processed = self.files_count - len(self.failed_files)
            f.write(f"{files_processed}/{self.files_count} files were processed.\n")
            for key, val in self.failed_files.items():
                f.write(f"FAILED file at: {key}, Error: {val}\n")
