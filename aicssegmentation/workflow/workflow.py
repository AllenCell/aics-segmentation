from typing import Any, Dict, List
import numpy as np
import logging
from aicsimageio import imread, AICSImage
from aicsimageio.writers import OmeTiffWriter

from .workflow_step import WorkflowStep
from .workflow_definition import WorkflowDefinition, PrebuiltWorkflowDefinition

from pathlib import Path
from os import listdir

log = logging.getLogger(__name__)

SUPPORTED_FILE_EXTENSIONS = [".tiff", ".tif", ".czi"]


class Workflow:
    """
    Represents an executable aics-segmentation workflow
    This class provides the functionality to run a workflow using an image input
    according to the steps defined in its WorkflowDefinition.
    """

    def __init__(self, workflow_definition: WorkflowDefinition, input_image: np.ndarray):
        if workflow_definition is None:
            raise ValueError("workflow_definition")
        if input_image is None:
            raise ValueError("image")
        self._definition: WorkflowDefinition = workflow_definition
        self._starting_image: np.ndarray = input_image
        self._next_step: int = 0  # Next step to execute
        self._results: List = list()  # Store step results

    @property
    def workflow_definition(self) -> WorkflowDefinition:
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

        result: np.ndarray = self.get_next_step().execute(image, parameters or step.parameter_values)
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

        self._files_count: int = 0
        self._failed_files: int = 0
        self._channel_index = channel_index
        self._log_file: Path = self.output_path.joinpath("log.txt")
        with open(self._log_file, "w") as log:
            log.write("Log for batch processing run")

    def is_valid_image(self, image_path: Path) -> bool:
        """
        Check if file at a given image_path and is a valid image type we support.

        Params:
            image_path (Path): image to check

        Returns:
            (bool): True if file has a supported file extension.
        """
        if not image_path.exists():
            return False
        if image_path.suffix.lower() in SUPPORTED_FILE_EXTENSIONS:
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

        files = [f for f in self.input_path.glob("**/*") if f.is_file]
        # Currently will save files in same format as they are in the input path
        for f in files:
            self._files_count += 1
            if self.is_valid_image(f):
                read_image = AICSImage(f)
                # read and format image in the way we expect
                image_from_path = self.format_image_to_3d(read_image)
                try:
                    # Run workflow on image
                    workflow = Workflow(self._workflow_definition, image_from_path)
                    result = workflow.execute_all()
                    with OmeTiffWriter(self.output_path.joinpath(f.name), overwrite_file=True) as w:
                        w.save(data=self.convert_bool_to_uint8(result), dimension_order="ZYX")

                except Exception as e:
                    # Handle failures during workflow execution/save
                    self._failed_files += 1
                    with open(self._log_file, "a") as log:
                        log.write(f"FAILED: {f}, ERROR: {e}")
            else:
                self._failed_files += 1
                with open(self._log_file, "a") as log:
                    log.write(f"FAILED: {f}, ERROR: Unsupported Image Type {f.suffix}")
        self._write_log_file_summary()

    def _write_log_file_summary(self):
        """
        Write a log file to the output folder.

        Params:
            none

        Returns:
            none
        """
        with open(self._log_file, "a") as f:
            if self._files_count == 0:
                f.write("There were no files to process in the input directory")
            else:
                files_processed = self._files_count - self._failed_files
                f.write(f"{files_processed}/{self._files_count} files were processed.\n")

    def format_image_to_3d(self, image: AICSImage) -> np.ndarray:
        """
        Format images in the way that aics-segmention expects for most workflows (3d, zyx)

        Params:
            image_path (AICSImage): image to format

        Returns:
            np.ndarray: segment-able image for aics-segmentation
        """
        if len(image.shape) == 6:
            # STCZYX
            return image.get_image_data("ZYX", C=self._channel_index, S=0, T=0)
        elif len(image.shape) == 5:
            if "S" in image.dims.order and "C" in image.dims.order:
                return image.get_image_data("ZYX", C=self._channel_index, S=0)
            elif "T" in image.dims.order and "C" in image.dims.order:
                return image.get_image_data("ZYX", C=self._channel_index, T=0)
            elif "S" in image.dims.order and "T":
                return image.get_image_data("ZYX", S=0, T=0)
        elif len(image.shape) == 4:
            return image.get_image_data("ZYX", C=self._channel_index)
        elif len(image.shape) == 3:
            return image.get_image_data("ZYX")
        else:
            return TypeError(f"Unsupported image format {image.dims.order}")

    def convert_bool_to_uint8(self, image: np.ndarray):
        """
        Format segmented images to uint8 to save via AICSImage

        Params:
            image (np.ndarray): segmented image

        Returns:
            np.ndarray: image converted to uint8 for saving
        """
        image = image.astype(np.uint8)
        image[image > 0] = 255
        return image
