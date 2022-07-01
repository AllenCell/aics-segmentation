import numpy as np
from typing import Union
from pathlib import Path

from aicssegmentation.core.seg_dot import dot_3d
from aicssegmentation.core.pre_processing_utils import (
    intensity_normalization,
    edge_preserving_smoothing_3d,
)
from skimage.morphology import remove_small_objects
from aicssegmentation.core.output_utils import (
    save_segmentation,
    generate_segmentation_contour,
)

from skimage.filters import threshold_otsu


def Workflow_PCNA_lateS_hole_fill(
    struct_img: np.ndarray,
    rescale_ratio: float = -1,
    output_type: str = "default",
    output_path: Union[str, Path] = None,
    fn: Union[str, Path] = None,
    output_func=None,
):
    """
    classic segmentation workflow wrapper for structure pcna

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
    """
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    ##########################################################################

    intensity_norm_param = [0.5, 15]
    intensity_norm_param_otsu = [0.5, 15]
    scaling_factor = 1.0
    minArea = 30
    dot_3d_sigma = 1.0
    otsumask_min_area = 50
    ##########################################################################

    out_img_list = []
    out_name_list = []

    ###################
    # PRE_PROCESSING
    ###################
    # intenisty normalization (min/max)
    struct_img = intensity_normalization(struct_img, scaling_param=intensity_norm_param)
    struct_img_otsu = intensity_normalization(struct_img, scaling_param=intensity_norm_param_otsu)

    out_img_list.append(struct_img.copy())
    out_name_list.append("im_norm")

    # smoothing with boundary preserving smoothing
    structure_img_smooth = edge_preserving_smoothing_3d(struct_img)
    structure_img_smooth_otsu = edge_preserving_smoothing_3d(struct_img_otsu)
   

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append("im_smooth")
    out_img_list.append(structure_img_smooth_otsu.copy())
    out_name_list.append("im_smooth_otsu")
   

    ###################
    # core algorithm
    ###################
    otsu_thresh = threshold_otsu(structure_img_smooth_otsu)
    global_thresh = otsu_thresh * scaling_factor
    bw_otsu_mask = structure_img_smooth_otsu > global_thresh
    bw_otsu_mask_removesmallobjects = remove_small_objects(
        bw_otsu_mask, min_size=otsumask_min_area, connectivity=1, in_place=False
    )


    response_s3_1 = dot_3d(structure_img_smooth, log_sigma=dot_3d_sigma)
    response_s3_2 = dot_3d(structure_img_smooth, log_sigma=2)

    bw_medium = response_s3_1 > 0.05
    bw_large =  response_s3_2 > 0.095
    bw_dots = np.logical_or(bw_medium, bw_large)
    bw = np.logical_and(bw_dots, bw_otsu_mask_removesmallobjects)
    
    out_img_list.append(bw_otsu_mask.copy())
    out_name_list.append("bw_otsu_mask")
    out_img_list.append(bw_otsu_mask_removesmallobjects.copy())
    out_name_list.append("bw_otsu_mask_removesmallobjects")
    out_img_list.append(bw.copy())
    out_name_list.append("bw")

    ###################
    # POST-PROCESSING
    ###################
    bw = remove_small_objects(bw > 0, min_size=minArea, connectivity=1, in_place=False)
    for zz in range(bw.shape[0]):
        bw[zz, :, :] = remove_small_objects(bw[zz, :, :], min_size=3, connectivity=1, in_place=False)

    segwithholes = remove_small_objects(bw > 0, min_size=minArea, connectivity=1, in_place=False)
    seg = ndimage.binary_fill_holes(segwithholes).astype(int)

    from aicssegmentation.core.utils import remove_hot_pixel

    seg = seg > 0
    seg_clean = remove_hot_pixel(seg)
    seg = seg_clean.astype(np.uint8)
    seg[seg > 0] = 255

    out_img_list.append(seg.copy())
    out_name_list.append("bw_final")

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
        raise NotImplementedError("invalid output type: {output_type}")
