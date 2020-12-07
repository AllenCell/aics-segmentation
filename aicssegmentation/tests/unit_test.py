import numpy as np
from aicsimageio import imread
from pathlib import Path
import importlib
from aicsimageio.writers import OmeTiffWriter

# import pytest
import os


DEFAULT_MODULE_PATH = "aicssegmentation.structure_wrapper.seg_"

ALL_STRUCTURE_NAMES = [
    "actb",
    "actn1",
    "atp2a2",
    "cardio_actn2",
    "cardio_atp2a2",
    "cardio_fbl",
    "cardio_fbl_100x",
    "cardio_myl7",
    "cardio_npm1",
    "cardio_npm1_100x",
    "cardio_tnni1",
    "cardio_ttn",
    "cetn2",
    "ctnnb1",
    "drug_npm1",
    "dsp",
    "fbl",
    "fbl_labelfree_4dn",
    "gja1",
    "h2b",
    "lamp1",
    # 'lmnb1_interphase',
    "lmnb1_mitotic",
    "myh10",
    "npm1",
    # 'npm1_SR',
    "npm_labelfree_4dn",
    "nup153",
    "pxn",
    "rab5a",
    "sec61b",
    "sec61b_dual",
    "slc25a17",
    "smc1a",
    "son",
    "st6gal1",
    "tjp1",
    "tomm20",
    "tuba1b",
    "ubtf",
]

TEST_IMG_DIR = "expected_output_images/"


# @pytest.fixture
# def data_dir() -> Path:
#     return Path(__file__).parent / "tests"


# change directories so pytest can find reference images
if not os.getcwd().endswith("tests"):
    os.chdir(os.getcwd() + "/aicssegmentation/tests")
    print("changing directory")


BASE_IMAGE_DIM = (128, 128, 128)
RESCALE_RATIO = 0.7


def create_random_source_image():
    random_array = np.random.rand(*BASE_IMAGE_DIM)

    # write numpy array to .tiff file
    with OmeTiffWriter(TEST_IMG_DIR + "random_input.tiff") as writer:
        writer.save(random_array)


def create_all_test_images():
    # create random input image to base segmentations on
    create_random_source_image()
    for structure_name in ALL_STRUCTURE_NAMES:
        print("Creating expected image for", structure_name, "...")
        create_test_image(structure_name, "default")


def create_test_image(structure_name: str, output_type: str = "default"):
    # load structure wrapper for specified structure
    structure_name = structure_name.lower()
    module_name = DEFAULT_MODULE_PATH + structure_name
    try:
        seg_module = importlib.import_module(module_name)
        function_name = "Workflow_" + structure_name
        SegModuleFunction = getattr(seg_module, function_name)
    except Exception as e:
        print(f"raising failure while trying to get module/function for {module_name}")
        raise e

    # load stock random image
    random_array = imread(Path(TEST_IMG_DIR + "random_input.tiff")).reshape(
        *BASE_IMAGE_DIM
    )

    # conduct segmentation
    output_array = SegModuleFunction(
        struct_img=random_array,
        rescale_ratio=RESCALE_RATIO,
        output_type=output_type,
        output_path=TEST_IMG_DIR,
        fn="expected_" + structure_name,
    )
    return output_array


def unit_test(structure_name: str):
    structure_name = structure_name.lower()
    # segment stock random image with current semgentation versions
    output_array = create_test_image(structure_name, output_type="array").ravel()

    # get rid of STC dimensions from AICSImage format, resized to resize_ratio
    expected_output = imread(
        Path(TEST_IMG_DIR + "expected_" + structure_name + "_struct_segmentation.tiff")
    ).ravel()

    assert np.allclose(output_array, expected_output), (
        "Tested and expected outputs differ for " + structure_name
    )


def test_all_structures():
    for structure_name in ALL_STRUCTURE_NAMES:
        print("Testing", structure_name, "...")
        unit_test(structure_name)


test_all_structures()
