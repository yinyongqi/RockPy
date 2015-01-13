__author__ = 'volk'
import matplotlib.pyplot as plt
import numpy as np

import base
from RockPy.Structure.data import RockPyData


class ThermoCurve(base.Measurement):
    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        self._data = {'up_temp': None,
                      'down_temp': None}

        super(ThermoCurve, self).__init__(sample_obj, mtype, mfile, machine)


    def format_vftb(self):
        data = self.machine_data.out_thermocurve()
        header = self.machine_data.header
        if len(data) > 2:
            print('LENGTH of machine.out_thermocurve =! 2. Assuming data[0] = heating data[1] = cooling')
            # self.log.warning('LENGTH of machine.out_thermocurve =! 2. Assuming data[0] = heating data[1] = cooling')
        if len(data) > 1:
            self._data['up_temp'] = RockPyData(column_names=header, data=data[0])
            self._data['down_temp'] = RockPyData(column_names=header, data=data[1])
        else:
            print('LENGTH of machine.out_thermocurve < 2.')
            # self.log.error('LENGTH of machine.out_thermocurve < 2.')

    def format_vsm(self):
        data = self.machine_data.out_thermocurve()
        header = self.machine_data.header
        segments = self.machine_data.segment_info

        aux = np.array([j for i in data for j in i])  # combine all data arrays
        a = np.diff(aux, axis=0)[:, 0]
        zero_crossings = np.where(np.diff(np.sign(a)))[0]  # indices of all zero crossings
        zero_crossings = [v+1 for i, v in enumerate(zero_crossings) if
                          np.diff(zero_crossings)[i - 1] > 0]  # get rid of temp jerks

        zero_crossings = [0] + zero_crossings  # start with zero index
        zero_crossings += [len(aux)] # append last index

        ut = 0 #running number warming
        dt = 0 # running number cooling

        for i, v in enumerate(zero_crossings):
            if v < zero_crossings[-1]: # prevents index Error
                if sum(a[v:zero_crossings[i+1]]) < 0: # cooling
                    name = 'cool%02i'%(ut)
                    ut += 1
                else:
                    name = 'warm%02i'%(dt)
                    dt += 1
                data = aux[v:zero_crossings[i+1]+1]
                rpd = RockPyData(column_names=header, data=data)
                rpd.rename_column('temperature', 'temp')
                rpd.rename_column('moment', 'mag')
                self._data.update({name: rpd})

        # ut = [i for i, v in enumerate(segments['initial temperature'].v)
        #       if segments['initial temperature'].v[i] < segments['final temperature'].v[i]
        # ]
        # dt = [i for i, v in enumerate(segments['initial temperature'].v)
        #       if segments['initial temperature'].v[i] > segments['final temperature'].v[i]]
        #
        # up_data = np.array([data[i] for i in ut])
        # up_data = [j for i in up_data for j in i]
        # down_data = [data[i] for i in dt]
        # down_data = [j for i in down_data for j in i]
        #
        # self._data['up_temp'] = RockPyData(column_names=header, data=up_data)
        # self._data['up_temp'].rename_column('temperature', 'temp')
        # self._data['up_temp'].rename_column('moment', 'mag')
        #
        # self._data['down_temp'] = RockPyData(column_names=header, data=down_data)
        # self._data['down_temp'].rename_column('temperature', 'temp')
        # self._data['down_temp'].rename_column('moment', 'mag')

    @property
    def ut(self):
        """
        returns a RPdata with all warming data
        """
        out = None
        for i in self._data:
            if 'warm' in i:
                if not out:
                    out = self._data[i]
                else:
                    out = out.append_rows(self._data[i])
        return out

    @property
    def dt(self):
        """
        returns a RPdata with all cooling data
        """
        out = None
        for i in self._data:
            if 'cool' in i:
                if not out:
                    out = self._data[i]
                else:
                    out = out.append_rows(self._data[i])
        return out

    def plt_thermocurve(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        color = {'warm':'r', 'cool':'b'}
        for seg in self._data:
            ax.plot(self.data[seg]['temp'].v, self.data[seg]['mag'].v, '.-', color=color[seg[:4]])
        ax.grid()
        # ax.axhline(0, color='#808080')
        # ax.axvline(0, color='#808080')

        unit = 'T'
        field = np.mean(self.ut['field'].v)

        if field < 0.01:
            field *= 1000.
            unit = 'mT'

        ax.text(0.01, 1.01, 'mean field: %.3f %s' % (field, unit),  # replace with data.unit
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax.transAxes,

        )
        ax.set_xlabel('Temperature [%s]' % ('C'))  # todo data.unit
        ax.set_ylabel('Magnetic Moment [%s]' % ('Am2'))  # todo data.unit
        ax.set_title('Thermocurve %s' % self.sample_obj.name)
        lims = ax.get_ylim()
        ax.set_ylim([0, lims[1]])
        plt.tight_layout()
        plt.show()
