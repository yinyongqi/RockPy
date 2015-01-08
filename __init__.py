__author__ = 'volk'
import RockPy.Functions.general
import Plotting
from RockPy.Structure.sample import Sample
from RockPy.Structure.samplegroup import SampleGroup
from RockPy.Structure.study import Study
from RockPy.Structure.data import RockPyData, condense
from RockPy.Measurements.base import Measurement
from file_operations import save, load
RockPy.Functions.general.create_logger('RockPy')

import os
from os.path import join
test_data_path = join(os.getcwd().split('RockPy')[0], 'RockPy', 'Tutorials', 'test_data')

#os.chdir(default_path)