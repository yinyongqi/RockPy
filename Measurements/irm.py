from Structure.rockpydata import rockpydata

__author__ = 'volk'
import base
import numpy as np
import Structure.data
import matplotlib.pyplot as plt


class Irm(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        super(Irm, self).__init__(sample_obj, mtype, mfile, machine)


    def format_vftb(self):
        data = self.machine_data.out_irm()
        header = self.machine_data.header()
        self.log.debug('FORMATTING << %s >> raw_data for << VFTB >> data structure' % ('IRM'))
        self.remanence = rockpydata(column_names=header, data=data[0])

    def format_vsm(self):
        raise NotImplemented


    def plt_irm(self):
        plt.title('IRM acquisition %s' % (self.sample_obj.name))
        std, = plt.plot(self.remanence['field'], self.remanence['mag'], zorder=1)
        plt.grid()
        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.xlabel('Field [%s]' % ('T'))  # todo data.unit
        plt.ylabel('Magnetic Moment [%s]' % ('Am^2'))  # todo data.unit
        plt.show()