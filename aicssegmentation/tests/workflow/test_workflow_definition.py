import pytest

from aicssegmentation.workflow.workflow_definition import WorkflowDefinition
from . import SUPPORTED_STRUCTURE_NAMES


class TestWorkflowDefinition:
    @pytest.mark.parametrize("workflow_name", SUPPORTED_STRUCTURE_NAMES)
    def test_all_thumbnails(self, workflow_name: str):
        definition = WorkflowDefinition(name=workflow_name, steps=list(), from_file=False)
        assert definition.thumbnail_pre is not None
        assert len(definition.thumbnail_pre.shape) >= 2
        assert definition.thumbnail_post is not None
        assert len(definition.thumbnail_post.shape) >= 2

    @pytest.mark.parametrize("workflow_name", SUPPORTED_STRUCTURE_NAMES)
    def test_all_diagrams(self, workflow_name: str):
        definition = WorkflowDefinition(name=workflow_name, steps=list(), from_file=False)
        assert definition.diagram_image is not None
        assert len(definition.diagram_image.shape) >= 2
