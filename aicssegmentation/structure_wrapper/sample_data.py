import os
from aicsimageio import imread
import numpy as np

__all__ = []

data_dir = os.path.abspath(os.path.dirname(__file__))
distribution_dir = os.path.join(data_dir, '..')


def _load(f):
    """

    Args:
        f: string
            file name

    Returns:
        img: ndarray
            Image that has been loaded

    """
    return np.squeeze(imread(os.path.join(os.path.split(
        os.path.dirname(__file__))[0], "..", "demo_data", f)))


def rab5_demo_data():
    return _load("RAB5_demo_data.tif")
