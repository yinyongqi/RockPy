__author__ = 'mike'
import base
import Features.af_demag
import RockPy.Tutorials.sample
import matplotlib.pyplot as plt
class AfDemag(base.Generic):
    _required = ['afdemag']

    def initialize_visual(self):
        self.add_plot()
        self.ax = self.figs[self.name][0].gca()
        self.standard_features = [self.feature_data]
        self.single_features = [self.feature_grid]

        self.xlabel = 'AF Field [mT]'
        self.ylabel = 'Moment'

    def plotting(self, samples, **plt_opt):
        for sample in samples:
            measurements = sample.get_measurements(mtype=AfDemag._required)
            for feat in self.standard_features:
                for m in measurements:
                    feat(m, **plt_opt)

    def legend(self):
        plt.legend(loc='best')

    def feature_data(self, afdemag_obj):
        afdemag_obj = afdemag_obj.normalize(**self.norm)
        line = Features.af_demag.field_mom(self.ax, afdemag_obj)
        self._add_line_text_dict(line)


def test():
    S = RockPy.Tutorials.sample.get_af_demag_sample()

    P = AfDemag(S)
    # P.feature_grid()
    P.show()


if __name__ == '__main__':
    test()