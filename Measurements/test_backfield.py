from unittest import TestCase
import RockPy as rp

__author__ = 'mike'


class TestBackfield(TestCase):
    def setUp(self):
        self.vsm_file = '../tutorials.rst/test_data/MUCVSM_test01.coe'
        self.VSM_test = rp.Sample('test')

    def test_format_vsm(self):
        self.VSM_coe = self.VSM_test.add_measurement(mtype='backfield', mfile=self.vsm_file, machine='vsm')