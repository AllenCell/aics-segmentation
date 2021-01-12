# aicssegmentation

[![Build Status](https://github.com/AllenCell/aics-segmentation/workflows/Build%20Main/badge.svg)](https://github.com/AllenCell/aics-segmentation/actions)
[![Documentation](https://github.com/AllenCell/aics-segmentation/workflows/Documentation/badge.svg)](https://AllenCell.github.io/aics-segmentation)
[![Code Coverage](https://codecov.io/gh/AllenCell/aics-segmentation/branch/main/graph/badge.svg)](https://codecov.io/gh/AllenCell/aics-segmentation)

Part 1 of Allen Cell and Structure Segmenter


---

This repository only has the code for the "Classic Image Segmentation Workflow" of Segmenter. The deep learning part can be found at [https://github.com/AllenCell/aics-ml-segmentation](https://github.com/AllenCell/aics-ml-segmentation)

We welcome feedback and submission of issues. Users are encouraged to sign up on our [Allen Cell Discussion Forum](https://forum.allencell.org/) for quesitons and comments.

## Installation

Our package is implemented in Python 3.6. Detailed instructions as below:

[Installation on Linux](./docs/installation_linux.md) (Ubuntu 16.04.5 LTS is the OS we used for development)

[Installation on MacOS](./docs/installation_mac.md)

[Installation on Windows](./docs/installation_windows.md)


## Use the package

Our package is designed (1) to provide a simple tool for cell biologists to quickly obtain intracellular structure segmentation with reasonable accuracy and robustness over a large set of images, and (2) to facilitate advanced development and implementation of more sophisticated algorithms in a unified environment by more experienced programmers.

Visualization is a key component in algorithm development and validation of results (qualitatively). Right now, our toolkit utilizes [itk-jupyter-widgets](https://github.com/InsightSoftwareConsortium/itk-jupyter-widgets), which is a very powerful visualization tool, primarily for medical data, which can be used in-line in Jupyter notebooks. Some cool demo videos can be found [here](https://www.youtube.com/playlist?list=PL2lHcsoU0YJsh6f8j2vbhg2eEpUnKEWcl).

### Part 1: Quick Start

After following the installation instructions above, users will find that the classic image segmentation workflow in the toolkit is:

1. formulated as a simple 3-step workflow for solving 3D intracellular structure segmentation problem using restricted number of selectable algorithms and tunable parameters
2. accompanied by a ["lookup table"](https://www.allencell.org/segmenter.html#lookup-table) with 20+ representative structure localization patterns and their results as a reference, as well as the Jupyter notebook for these workflows as a starting point.

Typically, we use Jupyter notebook as a "playground" to explore different algorithms and adjust the parameters. After determining the algorithms and parameters, we use Python scritps to do batch processing/validation on a large number of data. 

**You can find a [DEMO on a real example](https://github.com/AllenCell/aics-ml-segmentation/blob/master/docs/demo_1.md) on our tutorial page**

### Part 2: API  

The list of high-level wrappers/functions used in the package can be found at [AllenCell.github.io/aics-segmentation](https://AllenCell.github.io/aics-segmentation). 


## Object Identification: Bridging the gap between binary image (segmentation) and analysis

The current version of the Allen Cell Segmenter is primarily focusing on converting fluorescent images into binary images, i.e., the mask of the target structures separated from the background (a.k.a segmentation). But, the binary images themselves are not always useful, with perhaps the exception of visualization of the entire image, until they are converted into statistically sound numbers that are then used for downstream analysis. Often the desired numbers do not refer to all masked voxels in an entire image but instead to specific "objects" or groups of objects within the image. In our python package, we provide functions to bridge the gap between binary segmentation and downstream analysis via  **object identification**.

**[What is object identification?](https://github.com/AllenCell/aics-segmentation/blob/master/docs/object_identification.md)**


**[See a real demo in jupyter notebook to learn how to use the object identification functions](https://github.com/AllenCell/aics-segmentation/blob/master/lookup_table_demo/bridging_the_gap_between_binary_image_and_analysis.ipynb)**


## Citing Segmenter

If you find our segmenter useful in your research, please cite our bioRxiv paper:

> J. Chen, L. Ding, M.P. Viana, M.C. Hendershott, R. Yang, I.A. Mueller, S.M. Rafelski. The Allen Cell Structure Segmenter: a new open source toolkit for segmenting 3D intracellular structures in fluorescence microscopy images. bioRxiv. 2018 Jan 1:491035.


## Development
See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.


***Free software: Allen Institute Software License***

