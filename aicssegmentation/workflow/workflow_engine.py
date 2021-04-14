import json
import numpy

from pathlib import Path
from typing import List
from aicssegmentation.util.directories import Directories
from aicssegmentation.structure_wrapper_config.structure_config_utils import get_all_workflows_avail_in_json
from . import Workflow, WorkflowDefinition

class WorkflowEngine:
    def __init__(self):
        with open(Directories.get_structure_config_dir() / "all_functions.json") as file:
            self._all_functions_info = json.load(file)

        self._load_workflow_definitions()    
        
    @property
    def workflow_definitions(self) -> List[WorkflowDefinition]:
        pass

    def get_workflow(self, workflow_name: str) -> Workflow:
        pass

    def _load_workflow_definitions(self):
        self._workflow_definitions = list()
        available_workflows = get_all_workflows_avail_in_json()
        for name in available_workflows:
            # load json from config
            # map
                # self._workflow_definitions.append(WorkflowDefinition.from_json())
            pass
