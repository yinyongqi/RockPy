__author__ = 'volk'
import numpy as np
import matplotlib.pyplot as plt

import base
from RockPy.Structure.data import RockPyData
from scipy import stats


class Hysteresis(base.Measurement):
    """

    .. testsetup:: *

       >>> from Structure.sample import Sample
       >>> vftb_file = '../testing/test_data/MUCVFTB_test.hys'
       >>> sample = Sample(name='vftb_test_sample')
       >>> M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')


    """

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):

        self._data = {'up_field': None,
                      'down_field': None,
                      'virgin': None,
                      'msi': None}

        super(Hysteresis, self).__init__(sample_obj, mtype, mfile, machine, **options)
        self.paramag_correction = None
        self.standard_parameters.update({'ms': {'from_field': 70}})

    # ## formatting functions
    def format_vftb(self):
        data = self.machine_data.out_hysteresis()
        header = self.machine_data.header
        self.induced = RockPyData(column_names=header, data=data[0])
        dfield = np.diff(self.induced['field'].v)
        idx = [i for i in range(len(dfield)) if dfield[i] <= 0]
        idx += [max(idx) + 1]
        virgin_idx = range(0, idx[0])
        down_field_idx = idx
        up_field_idx = range(idx[-1], len(dfield) + 1)

        self.data['virgin'] = self.induced.filter_idx(virgin_idx)
        self.data['down_field'] = self.induced.filter_idx(down_field_idx)
        self.data['up_field'] = self.induced.filter_idx(up_field_idx)

    def format_vsm(self):
        header = self.machine_data.header
        segments = self.machine_data.segment_info

        if 'adjusted field' in header:
            header[header.index('adjusted field')] = 'field'
            header[header.index('field')] = 'uncorrected field'

        if 'adjusted moment' in header:
            header[header.index('moment')] = 'uncorrected moment'
            header[header.index('adjusted moment')] = 'moment'

        if len(segments['segment number'].v) == 3:
            self.data['virgin'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self.data['down_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[1])
            self.data['up_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[2])

        if len(segments['segment number'].v) == 2:
            self.data['virgin'] = None
            self.data['down_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self.data['up_field'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[1])

        if len(segments['segment number'].v) == 1:
            self.data['virgin'] = RockPyData(column_names=header, data=self.machine_data.out_hysteresis()[0])
            self.data['down_field'] = None
            self.data['up_field'] = None

        try:
            self.data['virgin'].rename_column('moment', 'mag')
        except AttributeError:
            pass

        try:
            self.data['up_field'].rename_column('moment', 'mag')
        except AttributeError:
            pass

        try:
            self.data['down_field'].rename_column('moment', 'mag')
        except AttributeError:
            pass

    def format_microsense(self):
        data = self.machine_data.out_hys()
        header = self.machine_data.header

        self.raw_data = RockPyData(column_names=header, data=data)
        dfield = np.diff(self.raw_data['raw_applied_field_for_plot_'])
        down_field_idx = [i for i in range(len(dfield)) if dfield[i] < 0]
        up_field_idx = [i for i in range(len(dfield)) if dfield[i] > 0]

        self.data['down_field'] = self.raw_data.filter_idx(down_field_idx)
        self.data['down_field'].define_alias('field', 'raw_applied_field_for_plot_')
        self.data['down_field'].define_alias('mag', 'raw_signal_mx')
        self.data['down_field']['field'] *= 0.1 * 1e-3  # conversion Oe to Tesla

        self.data['up_field'] = self.raw_data.filter_idx(up_field_idx)
        self.data['up_field'].define_alias('field', 'raw_applied_field_for_plot_')
        self.data['up_field'].define_alias('mag', 'raw_signal_mx')
        self.data['up_field']['field'] *= 0.1 * 1e-3  # conversion Oe to Tesla

    # ## calculations

    def irrev(self, **options):
        irrev = self.data['down_field']
        irrev -= self.data['up_field']
        return irrev

    # ## results

    def result_generic(self, parameters='standard', recalc=False, **options):
        '''
        Generic for for result implementation. Every calculation of result should be in the self.results data structure
        before calculation.
        It should then be tested if a value for it exists, and if not it should be created by calling
        _calculate_result_(result_name).

        '''
        self.calc_result(parameters, recalc)
        return self.results['generic']

    def result_ms(self, recalc=False, **parameter):
        """
        calculates the Ms value with a linear fit
        :param recalc:
        :param parameter:
            - from_field : field value in % of max. field above which slope seems linear
        :return:
        """
        self.calc_result(parameter, recalc)
        return self.results['ms']

    def result_sigma_ms(self, recalc=False, **parameter):
        self.calc_result(parameter, recalc, force_caller='ms')
        return self.results['sigma_ms']

    def result_mrs(self, recalc=False, **parameter):
        self.calc_result(dict(), recalc)
        return self.results['mrs']

    def result_sigma_mrs(self, recalc=False, **parameter):
        self.calc_result(dict(), recalc, force_caller='mrs')
        return self.results['sigma_mrs']

    def result_bc(self, recalc=False, **options):
        """
        Calculates :math:`B_c` using a linear interpolation between the points closest to zero.

        :param recalc: bool
                     Force recalculation if already calculated

        .. doctest::
           from Structure.project import Sample

           vftb_file = 'test_data/MUCVFTB_test.hys'
           sample = Sample(name='vftb_test_sample')
           M = sample.add_measurement(mtype='hysteresis', mfile=vftb_file, machine='vftb')
           M.result_bc()

           >>> 0.00647949
        """
        self.calc_result(dict(), recalc)
        return self.results['bc']

    def result_sigma_bc(self, recalc=False, **options):
        self.calc_result(dict(), recalc, force_caller='bc')
        return self.results['sigma_bc']

    def result_brh(self, recalc=False, **options):
        self.calc_result(dict(), recalc)
        return self.results['brh']

    def result_paramag_slope(self, from_field=80, recalc=False, **options):
        parameter = {'from_field': from_field
        }
        self.calc_result(parameter, recalc, force_caller='ms')
        return self.results['paramag_slope']

    # ## calculations

    def calculate_ms(self, **parameters):
        """
        Calculates the value for Ms
        :param parameters: from_field: from % of this value a linear interpolation will be calculated for all branches (+ & -)
        :return:
        """
        from_field = parameters.get('from_field', self.standard_parameters['ms']['from_field']) / 100.0
        df_fields = self.data['down_field']['field'].v / max(self.data['down_field']['field'].v)
        uf_fields = self.data['up_field']['field'].v / max(self.data['up_field']['field'].v)

        # get the indices of the fields larger that from_field
        df_plus = [i for i, v in enumerate(df_fields) if v >= from_field]
        df_minus = [i for i, v in enumerate(df_fields) if v <= -from_field]
        uf_plus = [i for i, v in enumerate(uf_fields) if v >= from_field]
        uf_minus = [i for i, v in enumerate(uf_fields) if v <= -from_field]

        dfp = self.data['down_field'].filter_idx(df_plus).lin_regress(column_name_x='field', column_name_y='mag')
        dfm = self.data['down_field'].filter_idx(df_minus).lin_regress(column_name_x='field', column_name_y='mag')
        ufp = self.data['down_field'].filter_idx(uf_plus).lin_regress(column_name_x='field', column_name_y='mag')
        ufm = self.data['down_field'].filter_idx(uf_minus).lin_regress(column_name_x='field', column_name_y='mag')
        self.paramag_correction = np.array([dfp, dfm, ufp, ufm])

        ms_all = [abs(dfp[2]), abs(dfm[2]), abs(ufp[2]), abs(ufm[2])]
        slope_all = [abs(dfp[0]), abs(dfm[0]), abs(ufp[0]), abs(ufm[0])]

        self.results['ms'] = np.median(ms_all)
        self.results['sigma_ms'] = np.std(ms_all)
        self.results['paramag_slope'] = np.median(slope_all)

        self.calculation_parameters['ms'] = parameters
        self.calculation_parameters['paramag_slope'] = parameters

    def calculate_mrs(self, **parameters):

        def calc(direction):
            d = getattr(self, direction)
            data = d['field'].v
            idx = np.argmin(abs(data))  # index of closest to 0
            if data[idx] < 0:
                if data[idx + 1] < 0:
                    idx1 = idx
                    idx2 = idx - 1
                else:
                    idx1 = idx + 1
                    idx2 = idx
            else:
                if data[idx + 1] < 0:
                    idx1 = idx + 1
                    idx2 = idx
                else:
                    idx1 = idx - 1
                    idx2 = idx

            i = [idx1, idx2]
            d = d.filter_idx(i)

            x = d['field'].v
            y = d['mag'].v
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            return abs(intercept)

        df = calc('down_field')
        uf = calc('up_field')
        self.results['mrs'] = np.mean([df, uf])
        self.results['sigma_mrs'] = np.std([df, uf])

    def calculate_bc(self, **parameters):
        '''

        :return:
        '''
        self.log.info('CALCULATING << Bc >> parameter from linear interpolation between points closest to m=0')

        def calc(direction):
            d = getattr(self, direction)
            data = d['mag'].v
            idx = np.argmin(abs(data))  # index of closest to 0
            if data[idx] < 0:
                if data[idx + 1] < 0:
                    idx1 = idx
                    idx2 = idx - 1
                else:
                    idx1 = idx + 1
                    idx2 = idx
            else:
                if data[idx + 1] < 0:
                    idx1 = idx + 1
                    idx2 = idx
                else:
                    idx1 = idx - 1
                    idx2 = idx

            i = [idx1, idx2]
            d = d.filter_idx(i)

            dy = d['mag'].v[1] - d['mag'].v[0]
            dx = d['field'].v[1] - d['field'].v[0]
            m = dy / dx
            b = d['mag'].v[1] - d['field'].v[1] * m
            bc = abs(b / m)

            return bc

        df = calc('down_field')
        uf = calc('up_field')
        self.results['bc'] = np.mean([df, uf])
        self.results['sigma_bc'] = np.std([df, uf])

    def calculate_brh(self, **parameters):
        pass  # todo implement

    def down_field_interp(self, **parameters):
        from scipy import interpolate

        x = self.data['down_field']['field'].v
        y = self.data['down_field']['mag'].v

        if np.all(np.diff(x) > 0):
            f = interpolate.interp1d(x, y, kind='slinear')
        else:
            x = x[::-1]
            y = y[::-1]
            f = interpolate.interp1d(x, y, kind='slinear')

        x_new = np.arange(min(x), max(x), 0.01)
        y_new = f(x_new)
        return x_new, y_new

    def up_field_interp(self, **parameters):
        from scipy import interpolate

        x = self.data['up_field']['field'].v
        y = self.data['up_field']['mag'].v

        if np.all(np.diff(x) > 0):
            f = interpolate.interp1d(x, y, kind='slinear')
        else:
            x = x[::-1]
            y = y[::-1]
            f = interpolate.interp1d(x, y, kind='slinear')

        x_new = np.arange(min(x), max(x), 0.01)
        y_new = f(x_new)
        return x_new, y_new

    def simple_paramag_cor(self, **parameters):

        if self.paramag_correction is None:
            self.calculate_ms(**parameters)

        slope = np.mean(self.paramag_correction[:, 0])
        intercept = np.mean(self.paramag_correction[:, 2])

        for dtype in self.data:
            if self.data[dtype]:
                d = self.data[dtype].v
                d[:, 1] -= d[:, 0] * slope

    # ## plotting functions
    def plt_hys(self):
        '''
        Rudimentary plotting function for quick check of data
        :return:
        '''

        std, = plt.plot(self.data['down_field']['field'].v, self.data['down_field']['mag'].v, '.-', zorder=1)
        plt.plot(self.data['up_field']['field'].v, self.data['up_field']['mag'].v, '.-',
                 color=std.get_color(),
                 zorder=1)
        plt.plot(0, self.results['mrs'].v[0], 'x')

        if not self.paramag_correction is None:
            slopes = self.paramag_correction[:, 0]
            intercepts = self.paramag_correction[:, 2]
            # downfield paramag_correction_line
            xdf = np.array([0, max(self.data['down_field']['field'].v)])  # get x
            xuf = np.array([min(self.data['down_field']['field'].v), 0])  # get x
            ydf = xdf * np.mean(slopes) + np.mean(np.fabs(intercepts))
            yuf = xuf * np.mean(slopes) - np.mean(np.fabs(intercepts))

            print np.mean(np.fabs(intercepts))
            print intercepts
            plt.plot(xdf, ydf, 'g--', alpha=0.5)
            plt.plot(xuf, yuf, 'g--', alpha=0.5)
        # plotting interpolated data
        # plt.plot(self.data['down_field']_interp()[0], self.data['down_field']_interp()[1], '--',
        # color=std.get_color(),
        # zorder=1)
        # plt.plot(self.data['up_field']_interp()[0], self.data['up_field']_interp()[1], '--',
        # color=std.get_color(),
        # zorder=1)

        if not self.data['virgin'] is None:
            plt.plot(self.data['virgin']['field'].v, self.data['virgin']['mag'].v, color=std.get_color(), zorder=1)

        # ## plotting pc as crosses
        # plt.plot([-(self.bc + (self.bc_diff / 2)), self.bc - (self.bc_diff / 2)], [0, 0], 'xr')
        plt.axhline(0, color='#808080')
        plt.axvline(0, color='#808080')
        plt.grid()
        plt.title('Hysteresis %s' % (self.sample_obj.name))
        plt.xlabel('Field [%s]' % ('T'))  # todo replace with data unit
        plt.ylabel('Moment [%s]' % ('Am2'))  # todo replace with data unit
        plt.show()

    def plt_hysteresis(self):
        '''
        helper calls plt_hys()
        :return:
        '''
        self.plt_hys()