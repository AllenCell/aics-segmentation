import numpy as np
from typing import Dict
import json
import importlib
from pathlib import Path, PurePosixPath
from aicssegmentation.structure_wrapper.WorkflowStep import WorkflowStep


def get_all_workflows_avail_in_json(return_list: bool = False):
    json_list = sorted(Path(__file__).parent.glob("conf_*.json"))
    all_names = [PurePosixPath(p.as_posix()).stem[5:] for p in json_list]
    print(all_names)

    if return_list:
        return all_names


def load_workflow_config(workflow_name: str):
    json_path = Path(__file__).parent / f"conf_{workflow_name}.json"
    with open(json_path, "r") as read_file:
        cfg = json.load(read_file)

    return cfg

def parse_config_to_objects(cfg: dict):
    workflow = list()
    for step in cfg.values():
        workflow.append(WorkflowStep(step))
    return workflow



def apply_on_single_image_with_config(img: np.ndarray, cfg: Dict):

    module_list = []
    out_list = [img]

    for (_, step_info) in cfg.items():
        module_name = importlib.import_module(step_info["module"])
        step_func = getattr(module_name, step_info["function"])
        module_list.append(step_func)
        if "parameter" in step_info:
            out = step_func(out_list[step_info["parent"]], **step_info["parameter"])
        else:
            out = step_func(out_list[step_info["parent"]])

        out_list.append(out)

    return out_list[-1]
