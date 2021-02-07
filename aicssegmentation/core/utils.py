from typing import List

import numpy as np
from scipy.ndimage import distance_transform_edt
from skimage.measure import label, regionprops
from skimage.morphology import ball, erosion, medial_axis


def hole_filling(
    bw: np.ndarray, hole_min: int, hole_max: int, fill_2d: bool = True
) -> np.ndarray:
    """Fill holes in 2D/3D segmentation

    Parameters:
    -------------
    bw: np.ndarray
        a binary 2D/3D image.
    hole_min: int
        the minimum size of the holes to be filled
    hole_max: int
        the maximum size of the holes to be filled
    fill_2d: bool
        if fill_2d=True, a 3D image will be filled slice by slice.
        If you think of a hollow tube alone z direction, the inside
        is not a hole under 3D topology, but the inside on each slice
        is indeed a hole under 2D topology.

    Return:
        a binary image after hole filling
    """
    bw = bw > 0
    if len(bw.shape) == 2:
        background_lab = label(~bw, connectivity=1)
        fill_out = np.copy(background_lab)
        component_sizes = np.bincount(background_lab.ravel())
        too_big = component_sizes > hole_max
        too_big_mask = too_big[background_lab]
        fill_out[too_big_mask] = 0
        too_small = component_sizes < hole_min
        too_small_mask = too_small[background_lab]
        fill_out[too_small_mask] = 0
    elif len(bw.shape) == 3:
        if fill_2d:
            fill_out = np.zeros_like(bw)
            for zz in range(bw.shape[0]):
                background_lab = label(~bw[zz, :, :], connectivity=1)
                out = np.copy(background_lab)
                component_sizes = np.bincount(background_lab.ravel())
                too_big = component_sizes > hole_max
                too_big_mask = too_big[background_lab]
                out[too_big_mask] = 0
                too_small = component_sizes < hole_min
                too_small_mask = too_small[background_lab]
                out[too_small_mask] = 0
                fill_out[zz, :, :] = out
        else:
            background_lab = label(~bw, connectivity=1)
            fill_out = np.copy(background_lab)
            component_sizes = np.bincount(background_lab.ravel())
            too_big = component_sizes > hole_max
            too_big_mask = too_big[background_lab]
            fill_out[too_big_mask] = 0
            too_small = component_sizes < hole_min
            too_small_mask = too_small[background_lab]
            fill_out[too_small_mask] = 0
    else:
        print("error in image shape")
        return

    return np.logical_or(bw, fill_out)


def topology_preserving_thinning(
    bw: np.ndarray, min_thickness: int = 1, thin: int = 1
) -> np.ndarray:
    """perform thinning on segmentation without breaking topology

    Parameters:
    --------------
    bw: np.ndarray
        the 3D binary image to be thinned
    min_thinkness: int
        Half of the minimum width you want to keep from being thinned.
        For example, when the object width is smaller than 4, you don't
        want to make this part even thinner (may break the thin object
        and alter the topology), you can set this value as 2.
    thin: int
        the amount to thin (has to be an positive integer). The number of
         pixels to be removed from outter boundary towards center.

    Return:
    -------------
        A binary image after thinning
    """
    bw = bw > 0
    safe_zone = np.zeros_like(bw)
    for zz in range(bw.shape[0]):
        if np.any(bw[zz, :, :]):
            ctl = medial_axis(bw[zz, :, :] > 0)
            dist = distance_transform_edt(ctl == 0)
            safe_zone[zz, :, :] = dist > min_thickness + 1e-5

    rm_candidate = np.logical_xor(bw > 0, erosion(bw > 0, ball(thin)))

    bw[np.logical_and(safe_zone, rm_candidate)] = 0

    return bw


def divide_nonzero(array1, array2):
    """
    Divides two arrays. Returns zero when dividing by zero.
    """
    denominator = np.copy(array2)
    denominator[denominator == 0] = 1e-10
    return np.divide(array1, denominator)


def histogram_otsu(hist):
    """ Apply Otsu thresholding method on 1D histogram """

    # modify the elements in hist to avoid completely zero value in cumsum
    hist = hist + 1e-5

    bin_size = 1 / (len(hist) - 1)
    bin_centers = np.arange(0, 1 + 0.5 * bin_size, bin_size)
    hist = hist.astype(float)

    # class probabilities for all possible thresholds
    weight1 = np.cumsum(hist)
    weight2 = np.cumsum(hist[::-1])[::-1]
    # class means for all possible thresholds

    mean1 = np.cumsum(hist * bin_centers) / weight1
    mean2 = (np.cumsum((hist * bin_centers)[::-1]) / weight2[::-1])[::-1]

    # Clip ends to align class 1 and class 2 variables:
    # The last value of `weight1`/`mean1` should pair with zero values in
    # `weight2`/`mean2`, which do not exist.
    variance12 = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2

    idx = np.argmax(variance12)
    threshold = bin_centers[:-1][idx]
    return threshold


def absolute_eigenvaluesh(nd_array):
    """Computes the eigenvalues sorted by absolute value from the symmetrical matrix.

    Parameters:
    -------------
    nd_array: nd.ndarray
        array from which the eigenvalues will be calculated.

    Return:
    -------------
        A list with the eigenvalues sorted in absolute ascending order (e.g.
        [eigenvalue1, eigenvalue2, ...])
    """
    eigenvalues = np.linalg.eigvalsh(nd_array)
    sorted_eigenvalues = sortbyabs(eigenvalues, axis=-1)
    return [
        np.squeeze(eigenvalue, axis=-1)
        for eigenvalue in np.split(
            sorted_eigenvalues, sorted_eigenvalues.shape[-1], axis=-1
        )
    ]


def sortbyabs(a, axis=0):
    """Sort array along a given axis by the absolute value
    modified from: http://stackoverflow.com/a/11253931/4067734
    """
    index = list(np.ix_(*[np.arange(i) for i in a.shape]))
    index[axis] = np.abs(a).argsort(axis)
    return a[index]


def get_middle_frame(struct_img: np.ndarray, method: str = "z") -> int:
    """find the middle z frame of an image stack

    Parameters:
    ------------
    struct_img: np.ndarray
        the 3D image to process
    method: str
        which method to use to determine the middle frame. Options
        are "z" or "intensity". "z" is solely based on the number of z
        frames. "intensity" method uses Otsu threshod to estimate the
        volume of foreground signals in the stack, then estimated volume
        of each z frame forms a z-profile, and finally another Otsu
        method is apply on the z profile to find the best z frame (with
        an assumption of two peaks along z profile, one near the bottom
        of the cells and one near the bottom of the cells, so the optimal
        separation is the middle of the stack).

    Return:
    -----------
    mid_frame: int
        the z index of the middle z frame
    """

    from skimage.filters import threshold_otsu

    if method == "intensity":
        bw = struct_img > threshold_otsu(struct_img)
        z_profile = np.zeros((bw.shape[0],), dtype=int)
        for zz in range(bw.shape[0]):
            z_profile[zz] = np.count_nonzero(bw[zz, :, :])
        mid_frame = round(histogram_otsu(z_profile) * bw.shape[0]).astype(int)

    elif method == "z":
        mid_frame = struct_img.shape[0] // 2

    else:
        print("unsupported method")
        quit()

    return mid_frame


def get_3dseed_from_mid_frame(
    bw: np.ndarray,
    stack_shape: List,
    mid_frame: int,
    hole_min: int,
    bg_seed: bool = True,
) -> np.ndarray:
    """build a 3D seed image from the binary segmentation of a single slice

    Parameters:
    ------------
    bw: np.ndarray
        the 2d segmentation of a single frame
    shape_3d: List
        the shape of original 3d image, e.g. shape_3d = img.shape
    frame_index: int
        the index of where bw is from the whole z-stack
    area_min: int
        any connected component in bw2d with size smaller than area_min
        will be excluded from seed image generation
    bg_seed: bool
        bg_seed=True will add a background seed at the first frame (z=0).

    """
    from skimage.morphology import remove_small_objects

    out = remove_small_objects(bw > 0, hole_min)

    out1 = label(out)
    stat = regionprops(out1)

    # build the seed for watershed
    seed = np.zeros(stack_shape)
    seed_count = 0
    if bg_seed:
        seed[0, :, :] = 1
        seed_count += 1

    for idx in range(len(stat)):
        py, px = np.round(stat[idx].centroid)
        seed_count += 1
        seed[mid_frame, int(py), int(px)] = seed_count

    return seed
