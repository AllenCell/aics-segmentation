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
        self.all_files = list()
        self.load_all_image(
            os.path.join(
                os.path.split(os.path.dirname(__file__))[0], "..", "demo_data"
            )
        )


    def _load(self, f):
        """

        Args:
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
        return self._load("RAB5_demo_data.tif")

    def make_load_image(self, filename):
        no_ext = filename.split('.')[0]
        func_to_run = "def " + no_ext + "(self):" + "\n" + "   return self._load(\"" + filename + "\")"
        exec(func_to_run)
        exec("self." + no_ext + " = types.MethodType(" + no_ext + ", self)")

    def load_all_image(self, path):
        for filename in os.listdir(path):
            no_ext = filename.split('.')[0]
            setattr(SampleData, no_ext, self.make_load_image(filename))
            self.all_files.append(no_ext)
