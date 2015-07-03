__author__ = 'volk'
import RockPy.Functions.general
import PlottingOLD
import logging
from RockPy.Structure.sample import Sample
from RockPy.Structure.samplegroup import SampleGroup
from RockPy.Structure.study import Study
from RockPy.Structure.data import RockPyData, condense
from RockPy.Measurements.base import Measurement
from RockPy.Structure.series import Generic as Series
from file_operations import save, load
from file_operations import get_fname_from_info, get_info_from_fname, import_folder

from RockPy.VisualizeV3 import NewFigure

RockPy.Functions.general.create_logger('RockPy')
logger = logging.getLogger('RockPy')


import matplotlib
logger.info('using matplotlib version %s' % matplotlib.__version__)

import numpy
logger.info('using numpy version %s' % numpy.__version__)

import os
from os.path import join

test_data_path = join(os.getcwd().split('RockPy')[0], 'RockPy', 'Tutorials', 'test_data')

# os.chdir(default_path)