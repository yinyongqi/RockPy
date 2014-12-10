from unittest import TestCase

__author__ = 'mike'

from unittest import TestCase
import RockPy as RP
import VisualizeV2.base
import matplotlib.pyplot as plt

__author__ = 'mike'



class TestGeneric(TestCase):

    def setUp(self):
        self.sample = RP.Sample(name='test_sample')
        self.sample.add_measurement(mtype='thellier', mfile='../testing/test_data/NLCRY_Thellier_test.TT',
                                    machine='cryomag')
        self.sample_group = RP.SampleGroup(sample_list=self.sample)
        self.Plot = VisualizeV2.base.Generic()


    def test_sample_names(self):
        self.Plot = VisualizeV2.base.Generic(plot_samples=self.sample)
        samples = ['test_sample']
        self.assertEqual(samples, self.Plot.sample_names)

    def test_samples(self):
        self.Plot = VisualizeV2.base.Generic(plot_samples=self.sample)
        samples = [self.sample]
        self.assertEqual(samples, self.Plot.samples)


    def test_sample_nr(self):
        self.Plot = VisualizeV2.base.Generic(plot_samples=self.sample)
        self.assertEqual(1, self.Plot.sample_nr)


    def test_add_plot(self):
        for i in range(1):
            self.Plot.add_plot(label='test')
        self.assertEqual(1, len(self.Plot.plots))
        self.assertTrue('test' in self.Plot.plots)
        # self.Plot.plots = None

    def test_show(self):
        # for i in range(1):
        #     self.Plot.add_plot(label='test')
        # self.Plot.show()
        pass

    def test_meets_requirements(self):
        Plot = VisualizeV2.Paleointensity.Arai(self.sample)
        self.assertTrue(Plot.meets_requirements(self.sample))
