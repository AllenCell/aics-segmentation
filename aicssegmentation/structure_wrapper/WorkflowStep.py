import importlib

class WorkflowStep:
    def __init__(self, step_config):
        self.name = step_config["name"]
        module = importlib.import_module(step_config["module"])
        self.function = getattr(module, step_config["function"])
        self.parameters = None
        if "parameter" in step_config:
            self.parameters = step_config["parameter"]
        self.parent = step_config["parent"]

    def execute(self, image):
        if self.parameters:
            return self.function(image, **self.parameters)
        else:
            return self.function(image)
