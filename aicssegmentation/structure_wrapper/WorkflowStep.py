class WorkflowStep:
    def __init__(self, step_config):
        self.name = step_config["name"]
        self.function = getattr(step_config["module"], step_config["function"])
        self.parameters = None
        if "parameter" in step_config:
            self.parameters = step_config["parameter"]
        self.parent = step_config["parent"]

    def execute(self, image):
        if self.parameters:
            return self.function(image, **self.parameters)
        else:
            return self.function(image)
