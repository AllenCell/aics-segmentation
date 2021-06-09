from aicssegmentation.workflow import WorkflowEngine
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    w = WorkflowEngine().get_executable_batch_workflow("sec61b", "/Users/sylvain.slaton/segmenter/input/", "/Users/sylvain.slaton/segmenter/output/")
    w.execute_all()