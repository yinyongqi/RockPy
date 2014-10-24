__author__ = 'mike'
import matplotlib.pyplot as plt

import base
import Plotting.af_demag


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
        self.show()

        self.x_label = 'AF-Field [%s]' % ('mT')  # todo get_unit
        self.y_label = 'Magnetic Moment [%s]' % ('Am^2')  # todo get_unit
        plt.title('%s' % " ,".join(self.sample_names))
        plt.ylim([0, 1])
        if style == 'publication':
            self.setFigLinesBW()

        self.out()

    def show(self):
        for sample, measurements in self.get_measurement_dict(mtype='afdemag').iteritems():
            for measurement in measurements:
                plt_opt = self.get_plt_opt(sample, measurements, measurement)
                norm_factor = self.get_norm_factor(measurement)
                Plotting.af_demag.field_mom(self.ax, measurement,
                                            component=self.component, norm_factor=norm_factor,
                                            **plt_opt)

    def get_norm_factor(self, measurement):
        if not self.norm:
            return [1, 1]
        if self.norm == 'max':
            nf = max(measurement.data[self.component])
            return [1, nf]
        if self.norm == 'mass':
            return [1, measurement.sample_obj.mass_kg]