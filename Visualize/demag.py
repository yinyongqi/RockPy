__author__ = 'mike'
import matplotlib.pyplot as plt

import RockPy.Plotting
from RockPy.Plotting import af_demag
import base


class AfDemag(base.Generic):
    def __init__(self, sample_list, norm='mass',
                 component='mag',
                 plot='show', folder=None, name='af-demagnetization',
                 plt_opt=None, style='screen',
                 **options):

        super(AfDemag, self).__init__(sample_list, norm=norm,
                                      plot=plot, folder=folder, name=name,
                                      plt_opt=plt_opt, style=style,
                                      **options)
        self.component = component
        self.show(**options)

        self.x_label = 'AF-Field [%s]' % ('mT')  # todo get_unit
        self.y_label = 'Magnetic Moment [%s]' % ('Am^2')  # todo get_unit
        plt.title('%s' % " ,".join(self.sample_names))
        # plt.ylim([0, 1])
        if style == 'publication':
            self.setFigLinesBW()

        self.out()

    def show(self, **options):
        mdf_line = options.get('mdf_line', True)
        mdf_text = options.get('mdf_text', False)
        shift = 0

        for sample, measurements in self.get_measurement_dict(mtype='afdemag').iteritems():
            for measurement in measurements:
                plt_opt = self.get_plt_opt(sample, measurements, measurement)
                norm_factor = self.get_norm_factor(measurement)
                RockPy.Plotting.af_demag.field_mom(self.ax, measurement,
                                            component=self.component, norm_factor=norm_factor,
                                            **plt_opt)
                if mdf_line:
                    RockPy.Plotting.af_demag.mdf_line(self.ax, measurement,
                                               component=self.component, norm_factor=norm_factor,
                                               **plt_opt)
                if mdf_text:
                    RockPy.Plotting.af_demag.mdf_txt(self.ax, measurement,
                                               component=self.component, norm_factor=norm_factor,
                                               y_shift = shift,
                                               **plt_opt)
                shift += 0.1


    def get_norm_factor(self, measurement):
        if not self.norm:
            return [1, 1]
        if self.norm == 'max':
            nf = max(measurement.data[self.component].v)
            return [1, nf]
        if self.norm == 'mass':
            return [1, measurement.sample_obj.mass_kg]