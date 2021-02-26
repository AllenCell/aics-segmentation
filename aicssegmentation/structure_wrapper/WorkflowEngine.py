class WorkflowEngine:
    def __init__(self, workflow_name, image):
        self.workflow_name = workflow_name
        self.steps = list()
        self.currentStep = 0
        self.image = [image]

    def get_next_step(self):
        return self.steps[self.currentStep]

    def execute_next(self):
        # Execute the next step and add result to results list
        self.image.append(self.execute_step())
        return self.image[-1]

    def execute_step(self):
        # Perform current step on last image result
        result = self.steps[self.currentStep].execute(self.image[-1])

        # Keep track of current step
        self.currentStep = self.currentStep + 1
        return result

    def see_result(self, step_index):
        # see the result of a step that has been run
        if step_index >= self.currentStep:
            # throw error
            print("cannot get result at this step, has not been run")
        else:
            return self.image[step_index]

