class WorkflowEngine:
    def __init__(self, workflow_name):
        self.workflow_name = workflow_name
        self.steps = list()
        self.currentStep = 0
        self.image = None

    def load_image(self):
        return 0

    def get_steps(self):
        return 0

    def apply_step(self):
        return 0

    def get_image(self):
        return self.image

    def get_next_step(self):
        return self.steps[self.currentStep]
