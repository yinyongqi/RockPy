__author__ = 'wack'


__author__ = 'wack'

import base
import numpy as np
from StringIO import StringIO

class Ani(base.Machine):
    """
    ani file format to describe anisotropy measurements
    format:
    first line: header / comment
    second line: reference/measurement directions in pairs of declination and inclinations (mdirs)
    i.e. D1,I1;D2,I2;D3,I3
    remaining lines 1 or 3 components of measurements
    i.e. V or x,y,z
    """

    def __init__(self, dfile, sample_name):
        super(Ani, self).__init__(dfile=dfile, sample_name=sample_name)

        # read the data file line by line
        f = open(self.file_name)
        self.raw_data = f.readlines()
        f.close()

        # store first header line
        self.header = self.raw_data[0]
        dipairs = self.raw_data[1].strip().split(';')
        self.mdirs = [[di[0], di[1]] for di in [dipair.split(',') for dipair in dipairs]]
        # read the directional values from remaining lines
        self.data = np.genfromtxt(StringIO(self.raw_data[2:]), delimiter=",")



