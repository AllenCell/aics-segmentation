from pathlib import Path, PurePosixPath


def get_all_workflows_avail_in_json(return_list: bool = False):
    json_list = sorted(Path(__file__).parent.glob("conf_*.json"))
    all_names = [PurePosixPath(p.as_posix()).stem[5:] for p in json_list] 
    print(all_names)

    if return_list:
        return all_names
