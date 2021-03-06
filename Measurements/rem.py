__author__ = 'mike'
import base
from copy import deepcopy
import numpy as np


class Rem_Prime(base.Measurement):
    _standard_parameter = {'rem_prime': {'b_min': 0, 'b_max': 90, 'component': 'mag',
                                         'interpolate': True, 'smoothing': 0}}

    def __init__(self, sample_obj,
                 machine='combined', mfile=None, mtype='rem_prime',
                 af1=None, af2=None,
                 **options):
        """
        :param sample_obj:
        :param mtype:
        :param mfile:
        :param machine:
        :param mdata: when mdata is set, this will be directly used as measurement data without formatting from file
        :param options:
        :return:
        """
        self.af1 = af1
        self.af2 = af2

        data = {'af1': af1.data, 'af2': af2.data}
        super(Rem_Prime, self).__init__(sample_obj=sample_obj, mtype=mtype, mfile=mfile, machine=machine, mdata=data)


    def result_rem_prime(self, component='mag', b_min=0, b_max=90, interpolate=True, smoothing=0, recalc=False, **opt):
        parameter = {'component': component,
                     'b_min': b_min,
                     'b_max': b_max,
                     'interpolate': interpolate,
                     'smoothing': smoothing,
        }
        self.calc_result(parameter, recalc)
        return self.results['rem_prime']

    def result_rem(self, component='mag', recalc=False, **opt):
        parameter = {'component': component,
        }
        self.calc_result(parameter, recalc)
        return self.results['rem']

    def calculate_rem_prime(self, **parameter):
        """
        :param parameter:
        """
        component = parameter.get('component', Rem_Prime._standard_parameter['rem_prime']['component'])
        ratios = self.calc_ratios(**parameter)
        self.results['rem_prime'] = np.mean(abs(ratios[component].v))



    def calc_ratios(self, **parameter):
        """
        calculates the ratio between the deriatives of two seperate AF demagnetization measurements
        :param parameter:
        :return:
        """
        b_min = parameter.get('b_min', Rem_Prime._standard_parameter['rem_prime']['b_min'])
        b_max = parameter.get('b_max', Rem_Prime._standard_parameter['rem_prime']['b_max'])
        component = parameter.get('component', Rem_Prime._standard_parameter['rem_prime']['component'])
        interpolate = parameter.get('interpolate', Rem_Prime._standard_parameter['rem_prime']['interpolate'])
        smoothing = parameter.get('smoothing', Rem_Prime._standard_parameter['rem_prime']['smoothing'])

        af1 = deepcopy(self.data['af1']['data'])
        af2 = deepcopy(self.data['af2']['data'])

        # truncate to within steps
        ### AF1
        idx = [i for i, v in enumerate(af1['field'].v) if b_min <= v <= b_max]
        if len(idx) != len(af1['field'].v):
            af1 = af1.filter_idx(idx)
        ### AF2
        idx = [i for i, v in enumerate(af2['field'].v) if b_min <= v <= b_max]
        if len(idx) != len(af2['field'].v):
            af2 = af2.filter_idx(idx)

        # find same fields
        b1 = set(af1['field'].v)
        b2 = set(af2['field'].v)

        if not b1 == b2:
            equal_fields = sorted(list(b1 & b1))
            interpolate_fields = sorted(list(b1 | b1))
            not_in_b1 = b1 - b2
            not_in_b2 = b2 - b1
            if interpolate:
                if not_in_b1:
                    af1 = af1.interpolate(new_variables=interpolate_fields)
                if not_in_b2:
                    af2 = af2.interpolate(new_variables=interpolate_fields)
            else:
                if not_in_b1:
                    idx = [i for i, v in enumerate(af1['field'].v) if v not in equal_fields]
                    af1 = af1.filter_idx(idx, invert=True)
                if not_in_b2:
                    idx = [i for i, v in enumerate(af2['field'].v) if v not in equal_fields]
                    af2 = af2.filter_idx(idx, invert=True)

        daf1 = af1.derivative(component, 'field', smoothing=smoothing)
        daf2 = af2.derivative(component, 'field', smoothing=smoothing)

        ratios = daf1 / daf2
        ratios.data = np.fabs(ratios.data) # no negatives
        return ratios

    def calc_rem_prime_field(self, add2resulrts = False, **parameter):
        component = parameter.get('component', Rem_Prime._standard_parameter['rem_prime']['component'])
        ratios = self.calc_ratios(**parameter)
        for i, v in enumerate(ratios['field'].v):
            name = 'rem\' [%.1f]' % v
            self.results = self.results.append_columns(column_names=name, data=abs(ratios[component].v[i]))
        return ratios

    def calculate_rem(self, **parameter):
        component = parameter.get('component', Rem_Prime._standard_parameter['rem_prime']['component'])

        af1 = deepcopy(self.data['af1']['data'])
        af2 = deepcopy(self.data['af2']['data'])

        rem = af1[component].v[0] / af2[component].v[0]
        self.results['rem'] = rem