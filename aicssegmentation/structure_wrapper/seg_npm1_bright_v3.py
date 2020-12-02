import numpy as np
from typing import Union
from pathlib import Path
from skimage.morphology import remove_small_objects
from aicssegmentation.core.pre_processing_utils import (
    intensity_normalization,
    edge_preserving_smoothing_3d
)
from aicssegmentation.core.seg_dot import dot_slice_by_slice
from skimage.filters import threshold_otsu
from aicssegmentation.core.output_utils import (
    save_segmentation,
    generate_segmentation_contour
)
from skimage.io import imread
from aicssegmentation.core.vessel import vesselnessSliceBySlice
from scipy.ndimage import zoom


def Workflow_npm1_bright_v3_single(
    struct_img: np.ndarray,
    rescale_ratio: float = -1,
    output_type: str = "default",
    output_path: Union[str, Path] = None,
    fn: Union[str, Path] = None,
    output_func=None
):
    """
    classic segmentation workflow wrapper for structure NPM1 bright v3 single

    Parameter:
    -----------
    struct_img: np.ndarray
        the 3D image to be segmented
    rescale_ratio: float
        an optional parameter to allow rescale the image before running the
        segmentation functions, default is no rescaling
    output_type: str
        select how to handle output. Currently, four types are supported:
        1. default: the result will be saved at output_path whose filename is
            original name without extention + "_struct_segmentaiton.tiff"
        2. array: the segmentation result will be simply returned as a numpy array
        3. array_with_contour: segmentation result will be returned together with
            the contour of the segmentation
        4. customize: pass in an extra output_func to do a special save. All the 
            intermediate results, names of these results, the output_path, and the
            original filename (without extension) will be passed in to output_func.

    no high level thresholding is used - step2
    """
    ##########################################################################
    # Basic PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [15, 5]
    # gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    # dot_2d_sigma = 2
    # dot_2d_sigma_extra = 3
    minArea = 8
    # low_level_min_size = 300
    ##########################################################################

    out_img_list = []
    out_name_list = []

    ###################
    # PRE_PROCESSING
    ###################
    # intenisty normalization (min/max)
    struct_img = intensity_normalization(struct_img, scaling_param=intensity_norm_param)

    out_img_list.append(struct_img.copy())
    out_name_list.append("im_norm")

    # rescale if needed
    if rescale_ratio > 0:
        struct_img = zoom(struct_img, (1, rescale_ratio, rescale_ratio), order=2)

        struct_img = (struct_img - struct_img.min() + 1e-8) / (
            struct_img.max() - struct_img.min() + 1e-8
        )
        gaussian_smoothing_truncate_range = (
            gaussian_smoothing_truncate_range * rescale_ratio
        )

    structure_img_smooth = edge_preserving_smoothing_3d(
        struct_img, numberOfIterations=10, conductance=1.2, timeStep=0.0625
    )

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append("im_smooth")

    ###################
    # core algorithm
    ###################
    # mitotic stage should align to folder name

    mito_seed_path_root = "/allen/aics/assay-dev/computational/data/Nucleus_structure_segmentation/trainset/NPM1_norm1/mem/"
    mito_seed_path = mito_seed_path_root + fn.replace(".tiff", ".mem_seg.tiff")
    # # mito_seed_path_root = "/allen/aics/assay-dev/computational/data/Nucleus_structure_segmentation/fibrillarin_segmentation_improvement/" + mitotic_stage + "/mito_seg/"
    # # mito_seed_path = mito_seed_path_root + fn + "_mem_segmentation.tif"

    # # Generate seed for mitotic cell
    mito_3d = imread(mito_seed_path)
    if np.ndim(mito_3d) == 4:
        mito_3d = mito_3d[:, :, :, 0]

    # specific case for presentation
    # mito_seed_path_root = '/allen/aics/assay-dev/computational/data/Nucleus_structure_segmentation/presentation/mem_seg/FBL_NPM1/'
    # mito_seed_path = mito_seed_path_root + fn.replace('.czi', '_mem_segmentation.tiff')
    # mito_3d = imread(mito_seed_path)
    # mito_3d = (mito_3d == 2).astype(np.uint8)
    ###############################

    bw_high_level = np.zeros_like(mito_3d)
    # lab_low, num_obj = label(bw_low_level, return_num=True, connectivity=1)
    # object_img = structure_img_smooth[mito_3d > 0]

    local_cutoff = threshold_otsu(structure_img_smooth)
    otsu_mito = threshold_otsu(structure_img_smooth[mito_3d > 0])

    # pdb.set_trace()
    local_diff = local_cutoff - otsu_mito
    # adaptive_factor = 0
    local_otsu = 0

    # vessel_cutoff = 0.95
    # slice_cutoff = 0.03
    # local_otsu = 1.9 * otsu_mito # It was 0.13
    # bw_high_level[np.logical_and(structure_img_smooth> local_otsu, mito_3d>0)]=1
    # bw_high_level = dilation(bw_high_level, selem=ball(1.5))

    if local_diff >= 0.33:
        vessel_cutoff = 0.045
        slice_cutoff = 0.03

    elif local_diff >= 0.10 and local_diff < 0.33:
        vessel_cutoff = 0.105
        slice_cutoff = 0.04
        local_otsu = 2.1 * otsu_mito
        bw_high_level[
            np.logical_and(structure_img_smooth > local_otsu, mito_3d > 0)
        ] = 1

    # When FBL seg is very brgiht
    elif local_diff < 0.05:
        vessel_cutoff = 0.15
        slice_cutoff = 0.06
        local_otsu = 2.5 * otsu_mito
        bw_high_level[
            np.logical_and(structure_img_smooth > local_otsu, mito_3d > 0)
        ] = 1

    # if local_diff >= 0.15:
    #     vessel_cutoff = 0.04
    #     slice_cutoff = 0.02

    # # When FBL seg is very brgiht
    # elif local_diff < 0.05:
    #     vessel_cutoff = 0.105
    #     slice_cutoff = 0.03
    #     local_otsu = 1.7 * otsu_mito
    #     bw_high_level[np.logical_and(structure_img_smooth> local_otsu, mito_3d>0)]=1

    # print(local_diff, local_otsu, np.percentile(structure_img_smooth[mito_3d>0],25))

    res3 = vesselnessSliceBySlice(structure_img_smooth, [1], tau=0.5, whiteonblack=True)
    res1 = dot_slice_by_slice(structure_img_smooth, 2)
    response_bright = np.logical_or(res1 > slice_cutoff, res3 > vessel_cutoff)
    total_bright = np.logical_or(response_bright, bw_high_level)

    bw_final = total_bright
    # pdb.set_trace()

    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(
        bw_final, min_size=minArea, connectivity=1, in_place=True
    )

    seg = seg > 0
    seg = seg.astype(np.uint8)
    seg[seg > 0] = 255

    out_img_list.append(seg.copy())
    out_name_list.append("bw_fine")

    fn = fn + "_npm_bright"

    if output_type == "default":
        # the default final output, simply save it to the output path
        save_segmentation(seg, False, Path(output_path), fn)
    elif output_type == "customize":
        # the hook for passing in a customized output function
        # use "out_img_list" and "out_name_list" in your hook to 
        # customize your output functions
        output_func(out_img_list, out_name_list, Path(output_path), fn)
    elif output_type == "array":
        return seg
    elif output_type == "array_with_contour":
        return (seg, generate_segmentation_contour(seg))
    else:
        raise NotImplementedError('invalid output type: {output_type}')

    # pdb.set_trace()
