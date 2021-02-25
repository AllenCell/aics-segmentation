class WorkflowStep:
    def __init__(self, step_config):
        self.name = step_config["name"]
        self.module = step_config["module"]
        self.function = step_config["function"]
        self.parameters = None
        if "parameter" in step_config:
            self.parameters = step_config["parameter"]
        self.parent = step_config["parent"]
