__author__ = 'volk'
import matplotlib.pyplot as plt

import base
from RockPy.Structure.data import RockPyData
import nrm


class Irm_Acquisition(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        self._data = {'remanence': None,
                      'induced': None}
        super(Irm_Acquisition, self).__init__(sample_obj, mtype, mfile, machine)


    def format_vftb(self):
        data = self.machine_data.get_data()
        header = self.machine_data.header
        # self.log.debug('FORMATTING << %s >> raw_data for << VFTB >> data structure' % (self.mtype))
        self._raw_data['remanence'] = RockPyData(column_names=header, data=data[0])

    def format_vsm(self):
        """
        formats the vsm output to be compatible with backfield measurements
        :return:
        """
        data = self.machine_data.out_backfield()
        header = self.machine_data.header

        #check for IRM acquisition
        if self.machine_data.measurement_header['SCRIPT']['Include IRM?'] == 'Yes':
            self._raw_data['remanence'] = RockPyData(column_names=['field', 'mag'], data=data[0][:, [0, 1]])

    def format_cryomag(self):
        #self.log.debug('FORMATTING << %s >> raw_data for << cryomag >> data structure' % (self.mtype))

        data = self.machine_data.out_trm()
        header = self.machine_data.float_header
        self._raw_data['remanence'] = RockPyData(column_names=header, data=data)
        self._raw_data['induced'] = None


    def plt_irm(self):
        plt.title('IRM acquisition %s' % (self.sample_obj.name))
        std, = plt.plot(self.remanence['field'].v, self.remanence['mag'].v, zorder=1)
        plt.grid()
        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.xlabel('Field [%s]' % ('T'))  # todo data.unit
        plt.ylabel('Magnetic Moment [%s]' % ('Am2'))  # todo data.unit
        plt.show()