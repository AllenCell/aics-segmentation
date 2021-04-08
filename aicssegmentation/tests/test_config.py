from pathlib import Path
import json


class TestConfig:
    def check_category_definition(self):
        json_list = sorted(Path("../structure_wrapper_config").glob("conf_*.json"))
        for workflow_config in json_list:
            with open(workflow_config, "r") as read_file:
                cfg = json.load(read_file)
            for step in cfg:
                assert (
                    "category" in cfg[step]
                ), f"Step {step} in {workflow_config} needs a category."

    def check_configs_match_all_functions(self):
        with open("../structure_wrapper_config/all_functions.json") as all_fctns_file:
            all_functions = json.load(all_fctns_file)
        json_list = sorted(Path("../structure_wrapper_config").glob("conf_*.json"))
        for workflow_config in json_list:
            with open(workflow_config, "r") as read_file:
                cfg = json.load(read_file)
            for step in cfg:
                step_name = cfg[step]["name"]

                # outside packages are not included in all_functions.json
                if "aicssegmentation" not in cfg[step]["module"]:
                    continue
                # all functions used in configs must be defined in all_functions.json
                assert (
                    step_name in all_functions.keys()
                ), f'Function "{step_name}" in workflow {workflow_config} is not in all_functions.json'

                # Check that functions with matching names import the same module
                reference_import = (
                    all_functions[step_name]["module"]
                    + all_functions[step_name]["function"]
                )
                import_name = cfg[step]["module"] + cfg[step]["function"]
                assert (
                    import_name == reference_import
                ), f"Import statement for {step_name} in workflow {workflow_config}, {import_name}, should match {reference_import} "

                # check that the parameters in the config file match the parameters required in all_functions.json
                reference_parameters = all_functions[step_name]["parameter"]
                if "parameter" in cfg[step]:
                    for param in cfg[step]["parameter"]:
                        assert (
                            param in reference_parameters.keys()
                        ), f'Parameter "{param}" in {workflow_config} is not defined for function {step_name}'
