from pathlib import Path
import numpy as np
from skimage.morphology import erosion, ball
from aicsimageio.writers import OmeTiffWriter


def save_segmentation(bw, contour_flag, output_path: Path, fn):
    with OmeTiffWriter(str(output_path / (fn + "_struct_segmentation.tiff"))) as writer:
        writer.save(bw)

    if contour_flag:
        bd = generate_segmentation_contour(bw)

        with OmeTiffWriter(str(output_path / (fn + "_struct_contour.tiff"))) as writer:
            writer.save(bd)


def generate_segmentation_contour(im):

    bd = np.logical_xor(erosion(im > 0, selem=ball(1)), im > 0)

    bd = bd.astype(np.uint8)
    bd[bd > 0] = 255

    return bd


# ### general hook for cutomized output ######
def output_hook(im, names, out_flag, output_path, fn):
    assert len(im) == len(names) and len(names) == len(out_flag)

    for i in range(len(out_flag)):
        if out_flag[i]:
            if names[i].startswith("bw_"):
                segmentation_type = names[i]
                bw = im[i].astype(np.uint8)
                bw[bw > 0] = 255
                with OmeTiffWriter(
                    str(output_path / (fn + "_bw_" + segmentation_type[3:] + ".tiff"))
                ) as writer:
                    writer.save(bw)
            else:
                with OmeTiffWriter(
                    str(output_path / (fn + "_" + names[i] + ".tiff"))
                ) as writer:
                    writer.save(im[i])


def paperFigure(out_img_list, out_name_list, output_type, output_path, fn):
    out_flag = []
    for i in range(len(out_name_list)):
        if out_name_list[i] == "im_smooth":
            out_flag.append(True)
        else:
            out_flag.append(False)

    out_flag[-1] = True  # also output the last one (always the final result)
    out_name_list[-1] = "struct_segmentation"  # use default name
    output_hook(out_img_list, out_name_list, out_flag, output_path, fn)


def QCB_simple(out_img_list, out_name_list, output_path, fn):
    out_flag = []
    for i in range(len(out_name_list)):
        out_flag.append(False)

    out_flag[-1] = True  # also output the last one (always the final result)
    out_name_list[-1] = "struct_segmentation"  # use default name
    output_hook(out_img_list, out_name_list, out_flag, output_path, fn)

    img_list = [out_img_list[-1]]
    name_list = [out_name_list[-1]]

    return img_list, name_list


def QCB_granularity(out_img_list, out_name_list, output_path, fn):

    out_flag = []
    img_list = []
    name_list = []
    for i in range(len(out_name_list)):
        if out_name_list[i] == "bw_coarse":
            out_flag.append(True)
            bw = out_img_list[i].astype(np.uint8)
            bw[bw > 0] = 255
            out_img_list[i] = bw
            out_name_list[i] = "struct_segmentation_coarse"
            img_list.append(bw)
            name_list.append("struct_segmentation_coarse")
        elif out_name_list[i] == "bw_fine":
            out_flag.append(True)
            bw = out_img_list[i].astype(np.uint8)
            bw[bw > 0] = 255
            out_img_list[i] = bw
            out_name_list[i] = "struct_segmentation_fine"
            img_list.append(bw)
            name_list.append("struct_segmentation_fine")
        else:
            out_flag.append(False)

    output_hook(out_img_list, out_name_list, out_flag, output_path, fn)
    return img_list, name_list
