import os
from aicsimageio import imread
import numpy as np
import types

__all__ = []


class SampleData:
    """
    A class that defines functions that grab sample data from the AICS-segmentation package
    """

    def __init__(self):
        """
        Constructor for the SampleData class

        Params:
        """
        self.all_func = list()  # List of available functions to call
        self.load_all_image(
            os.path.join(os.path.split(os.path.dirname(__file__))[0], "..", "demo_data")
        )

    def _load(self, f):
        """
        Load an image from the data demo folder
        Params:
            f: string
                file name

        Returns:
            img: ndarray
                Image that has been loaded
        """

        return np.squeeze(
            imread(
                os.path.join(
                    os.path.split(os.path.dirname(__file__))[0], "..", "demo_data", f
                )
            )
        )

    def rab5_demo_data(self):
        """
        Test function, load rab5_demo_data and provide and ndarray.
        Params:
            f: string
                file name

        Returns:
            img: ndarray
                Image that has been loaded
        """
        return self._load("RAB5_demo_data.tif")

    def make_load_image(self, filename):
        """
        Function generator to expose all images as python functions.
        call the generated function for the image by using
        imagename()
        Params:
            filename: string
                full filename of image in sample_data folder to expose

        Returns:
            none
        """
        no_ext = filename.split(".")[0]
        func_to_run = (
            "def "
            + no_ext
            + "(self):"
            + "\n"
            + '   return self._load("'
            + filename
            + '")'
        )
        exec(func_to_run)
        exec("self." + no_ext + " = types.MethodType(" + no_ext + ", self)")

    def load_all_image(self, path):
        """
        Expose all images in the path as python functions for the SampleData class
        Params:
            path: string
                path

        Returns:
            none
        """
        for filename in os.listdir(path):
            no_ext = filename.split(".")[0]
            setattr(SampleData, no_ext, self.make_load_image(filename))
            self.all_files.append(no_ext)
