from aicssegmentation.structure_wrapper_config.structure_config_utils import load_workflow_config, parse_config_to_objects


class WorkflowEngine:
    def __init__(self, workflow_name, image):
        self.workflow_name = workflow_name
        self.steps = self.get_steps()
        self.currentStep = 0
        self.starting_image = image

    def get_steps(self):
        return parse_config_to_objects(load_workflow_config(self.workflow_name))

    def get_next_step(self):
        return self.steps[self.currentStep]

    def execute_next(self):
        # Execute the next step and add result to results list
        if self.currentStep == 0:
            return self.execute_step(self.starting_image)
        elif self.currentStep > len(self.steps):
            print("No steps left to run")
        else:
            return self.execute_step(self.steps[self.currentStep - 1].result)

    def execute_step(self, image):
        # Perform current step on last image result
        result = self.steps[self.currentStep].execute(image)

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

    def see_most_recent_result(self):
        if self.currentStep == 0:
            return self.starting_image
        else:
            return self.steps[self.currentStep - 1].result

    def execute_all(self):
        while self.currentStep <= len(self.steps):
            self.execute_next()
        return self.image[-1]

