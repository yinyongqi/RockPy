__author__ = 'Wack'

from unittest import TestCase
import cryomag
import pmd


class TestCryoMag(TestCase):
    def setUp(self):
        self.file = '../tutorials.rst/test_data/NLCRYO_test.af'

    def test___init__(self):
        self.CMag_obj = cryomag.CryoMag(dfile=self.file, sample_name='DA6B')

    def test_float_header(self):
        self.test___init__()
        correct_header = ['step' 'coreaz' 'coredip' 'bedaz' 'beddip' 'vol' 'weight' 'x' 'y' 'z' 'm'
                          'sm' 'a95' 'dc' 'ic' 'dg']
        self.assertEqual(correct_header, self.CMag_obj.float_header)


class TestPMD(TestCase):
    def setUp(self):
        self.file = '../tutorials.rst/test_data/HA2A.pmd'

    def test___init__(self):
        self.PMD_obj = pmd.PMD(dfile=self.file, sample_name='HA2A')

    def test_sthg(self):
        pass
