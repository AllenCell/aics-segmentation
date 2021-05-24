import json
from json import JSONDecodeError

import numpy as np

from typing import List, Union
from .workflow import Workflow, BatchWorkflow

from .workflow_definition import WorkflowDefinition
from .workflow_config import WorkflowConfig
from pathlib import Path


class WorkflowEngine:
    """
    aicssegmentation workflow engine
    Use this class to access and execute aicssegmentation structure workflows
    """

    def __init__(self, workflow_config: WorkflowConfig = None):
        self._workflow_config = workflow_config or WorkflowConfig()
        self._workflow_definitions = self._load_workflow_definitions()

    @property
    def workflow_definitions(self) -> List[WorkflowDefinition]:
        """
        List of all workflow definitions
        """
        return self._workflow_definitions

    def get_executable_workflow(self, workflow_name: str, input_image: np.ndarray) -> Workflow:
        """
        Get an executable workflow object

        inputs:
            workflow_name (str): Name of the workflow to load
            input_image (ndarray): input image for the workflow to execute on
        """
        if input_image is None:
            raise ValueError("input_image is None")

        definition = next(filter(lambda d: d.name == workflow_name, self._workflow_definitions), None)
        if definition is None:
            raise ValueError(
                f"No available workflow definition found for {workflow_name}. Specify a valid workflow name."
            )

        return Workflow(definition, input_image)

    def get_executable_batch_workflow(self, workflow_name: str, input_dir: str, output_dir: str, channel_index: int):
        """
        Get an executable BatchWorkflow object

        inputs:
            workflow_name (str): Name of the workflow to load
            input_dir (str): input path where files to process are located
            output_dir (str): output path to write results to
            channel_index (int): index of selected channel
        """
        definition = next(filter(lambda d: d.name == workflow_name, self._workflow_definitions), None)
        if definition is None:
            raise ValueError(
                f"No available workflow definition found for {workflow_name}. Specify a valid workflow name."
            )

        return BatchWorkflow(definition, input_dir, output_dir, channel_index)

    def load_workflow_def(self, file_path: Path) -> WorkflowDefinition:
        if not file_path.exists():
            raise FileNotFoundError(f"Did not find a file at {file_path}")
        if file_path.suffix.lower() != ".json":
            raise ValueError(f"The file at {file_path} is not a json file.")

        with open(file_path) as f:
            try:
                data = json.load(f)
            except JSONDecodeError:
                raise ValueError("Invalid json file given, please validate before using")
        return self._structure_config.workflow_decoder(data, file_path.stem, from_file=True)

    def get_executable_workflow_from_config_file(
        self, file_path: Union[str, Path], input_image: np.ndarray
    ) -> Workflow:
        """
        Get an executable workflow object from a configuration file

        inputs:
            file_path (str|Path): Path to the workflow configuration file
            input_image (ndarray): input image for the workflow to execute on
        """
        if input_image is None:
            raise ValueError("input_image is None")
        if file_path is None:
            raise ValueError("file_path is None")

        definition = self._workflow_config.get_workflow_definition_from_config_file(Path(file_path))
        return Workflow(definition, input_image)

    def get_executable_batch_workflow_from_file(
        self, file_path: str, input_image: np.ndarray, input_dir: str, output_dir: str, channel_index: int
    ):
        if input_image is None:
            raise ValueError("input_image")
        norm_path = Path(file_path)
        definition = self.load_workflow_def(norm_path)
        return BatchWorkflow(definition, input_dir, output_dir, channel_index)

    def save_workflow_definition(self, workflow_definition: WorkflowDefinition, output_file_path: Union[str, Path]):
        if workflow_definition is None:
            raise ValueError("workflow_definition is None")
        if output_file_path is None:
            raise ValueError("file_path is None")

        self._workflow_config.save_workflow_definition_as_json(workflow_definition, output_file_path)

    def _load_workflow_definitions(self) -> List[WorkflowDefinition]:
        definitions = list()
        available_workflows = self._workflow_config.get_available_workflows()
        for name in available_workflows:
            definitions.append(self._workflow_config.get_workflow_definition(name))
        return definitions
