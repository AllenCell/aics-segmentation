from typing import Type
import numpy as np
import pytest

from unittest import mock
from aicsimageio.writers import OmeTiffWriter
from pathlib import Path
from aicsimageio import AICSImage
from numpy import random
from aicssegmentation.workflow.batch_workflow import BatchWorkflow
from aicssegmentation.workflow.workflow_config import WorkflowConfig


@pytest.fixture
def batch_workflow(tmp_path: Path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(0, 10):
        three_d_image = np.zeros((10, 100, 100))
        with OmeTiffWriter(input_dir / f"test{i}.tiff", overwrite_file=True) as w:
            w.save(data=three_d_image, dimension_order="ZYX")

    definition = WorkflowConfig().get_workflow_definition("sec61b")
    return BatchWorkflow(definition, input_dir, output_dir, channel_index=0)


class TestBatchWorkflow:
    @pytest.mark.parametrize("file_name", ["non_existant_image.tiff", "bad_extension.abc"])
    def test_is_valid_image(self, file_name, batch_workflow: BatchWorkflow):
        # batch_workflow = self._get_batch_workflow(tmp_path)
        input_dir = batch_workflow.input_dir

        assert not batch_workflow.is_valid_image(input_dir / file_name)
        assert batch_workflow.is_valid_image(input_dir / "test1.tiff")
        assert batch_workflow.is_valid_image(input_dir / "test2.tiff")
        assert batch_workflow.is_valid_image(input_dir / "test3.tiff")

    def test_format_image_to_3d(self, batch_workflow: BatchWorkflow):
        three_d_image = AICSImage(random.random((2, 3, 4)), known_dims="ZYX")

        assert len(batch_workflow.format_image_to_3d(three_d_image).shape) == 3

    def test_format_image_to_3d_timeseries(self, batch_workflow: BatchWorkflow):
        image = AICSImage(np.ones((1, 5, 1, 10, 100, 100)), known_dims="STCZYX")
        with pytest.raises(ValueError):
            batch_workflow.format_image_to_3d(image)

    def test_format_image_to_3d_multiscene(self, batch_workflow: BatchWorkflow):
        image = AICSImage(np.ones((5, 1, 1, 10, 100, 100)), known_dims="STCZYX")
        with pytest.raises(ValueError):
            batch_workflow.format_image_to_3d(image)

    def test_convert_bool_to_uint8(self, batch_workflow: BatchWorkflow):
        array_to_test = np.zeros((5))
        array_to_test.data[0] = 1
        array_to_test.data[4] = 1
        converted = batch_workflow.convert_bool_to_uint8(array_to_test)

        assert np.array_equal(converted, [255, 0, 0, 0, 255])

    @mock.patch("aicssegmentation.workflow.batch_workflow.Workflow.execute_all")
    def test_process_all(self, mock_workflow_execute_all, batch_workflow: BatchWorkflow):
        # Arrange
        mock_workflow_execute_all.return_value = np.zeros((10, 100, 100))

        # Act
        batch_workflow.process_all()

        # Assert
        assert batch_workflow.output_dir.exists()
        batch_workflow.output_dir.joinpath("log.txt").exists()
        assert len(list(batch_workflow.output_dir.glob("*.tiff"))) == 10
