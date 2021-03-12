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

def parse_config_to_objects(cfg: Dict):
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
        print(step_info["parent"])

        if type(step_info["parent"]) == list:
            inputs = [out_list[i] for i in step_info["parent"]]
        else:
            inputs = [out_list[step_info["parent"]]]

        if "parameter" in step_info:
            out = step_func(*inputs, **step_info["parameter"])
        else:
            out = step_func(*inputs)

        # if out returns multiple objects, store them in neighboring indices
        if type(out) == tuple:
            out = list(out)
            out_list += out
        else:
            out_list.append(out)
    return out_list[-1]


# cfg = load_workflow_config("npm1")
# img = np.random.randn(60, 60, 60)
# apply_on_single_image_with_config(img, cfg)
# print("done")
