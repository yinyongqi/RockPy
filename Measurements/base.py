__author__ = 'volk'
import logging
import inspect

import Functions.general
import Readin.base
from Structure.rockpydata import RockPyData
from Treatments.base import Generic
from Readin import *


class Measurement(object):
    Functions.general.create_logger('RockPy.MEASUREMENT')

    def __init__(self, sample_obj,
                 mtype, mfile, machine,
                 **options):
        """

        :param sample_obj:
        :param mtype:
        :param mfile:
        :param machine:
        :param suffix: str
        :param options:
        :return:
        """
        self.log = logging.getLogger('RockPy.MEASUREMENT.' + type(self).__name__)
        self.has_data = True

        # setting implemented machines
        # looking for all subclasses of Readin.base.Machine
        # generating a dictionary of implemented machines : {implemented out_* method : machine_class}
        implemented_machines = [cls for cls in Readin.base.Machine.__subclasses__()]
        self.implemented = {
            cls.__name__.lower(): {'_'.join(i.split('_')[1:]).lower(): cls for i in dir(cls) if i.startswith('out_')}
            for cls in implemented_machines}
        ''' initialize parameters '''
        self.machine_data = None  # returned data from Readin.machines()
        self.suffix = options.get('suffix', '')
        self.treatments = []

        ''' initial state '''
        self.is_machine_data = None  # returned data from Readin.machines()
        self.initial_state = None

        if machine in self.implemented:
            self.machine = machine.lower()
            if mtype.lower() in self.implemented[machine]:
                # self.log.debug('FOUND\t measurement type: << %s >>' % mtype.lower())
                self.mtype = mtype.lower()
                self.sample_obj = sample_obj
                self.mfile = mfile

                if self.machine and self.mfile:
                    self.import_data()
                    self.has_data = self.machine_data.has_data
                else:
                    self.log.debug('NO machine or mfile passed -> no raw_data will be generated')
            else:
                self.log.error('UNKNOWN\t measurement type: << %s >>' % mtype)
        else:
            self.log.error('UNKNOWN\t machine << %s >>' % self.machine)

        # dynamic data formatting
        # checks is format_'machine_name' exists. If exists it formats self.raw_data according to format_'machine_name'
        if callable(getattr(self, 'format_' + machine)):
            if self.has_data:
                self.log.debug('FORMATTING raw data from << %s >>' % machine)
                getattr(self, 'format_' + machine)()
            else:
                self.log.debug('NO raw data transfered << %s >>' % machine)

        else:
            self.log.error(
                'FORMATTING raw data from << %s >> not possible, probably not implemented, yet.' % self.machine)

        # dynamical creation of entries in results data. One column for each results_* method.
        # calculation_* methods are not creating columns -> if a result is calculated a result_* method
        # has to be written
        self.result_methods = [i[7:] for i in dir(self) if i.startswith('result_') if
                               not i.endswith('generic')]  # search for implemented results methods
        self.results = RockPyData(
            column_names=self.result_methods)  # dynamic entry creation for all available result methods

        # ## warning with calculation of results:
        # M.result_slope() -> 1.2
        # M.calculate_vds(t_min=300) -> ***
        # M.results['slope'] -> 1.2
        # M.result_slope(t_min=300) -> 0.9
        #
        # the results are stored for the calculation parameters that were used to calculate it.
        # This means calculating a different result with different parameters can lead to inconsistencies.
        # One has to be aware that comparing the two may not be useful

        # dynamically generating the calculation and standard parameters for each calculation method.
        # This just sets the values to non, the values have to be specified in the class itself
        self.calculation_methods = [i for i in dir(self) if i.startswith('calculate_') if not i.endswith('generic')]
        self.calculation_parameters = {i[10:]: None for i in self.calculation_methods}
        self.standard_parameters = {i[10:]: None for i in dir(self) if i.startswith('calculate_') if
                                    not i.endswith('generic')}

    def import_data(self, rtn_raw_data=None, **options):
        '''
        Importing the data from dfile and machine
        :param rtn_raw_data:
        :param options:
        :return:
        '''

        self.log.info(' IMPORTING << %s , %s >> data' % (self.machine, self.mtype))

        machine = options.get('machine', self.machine)
        mtype = options.get('mtype', self.mtype)
        mfile = options.get('mfile', self.mfile)
        raw_data = self.implemented[machine][mtype](mfile, self.sample_obj.name)
        if raw_data is None:
            self.log.error('IMPORTING\t did not transfer data - CHECK sample name and data file')
            return
        else:
            if rtn_raw_data:
                self.log.info(' RETURNING raw_data for << %s , %s >> data' % (machine, mtype))
                return raw_data
            else:
                self.machine_data = raw_data


    def set_initial_state(self,
                          mtype, mfile, machine,  # standard
                          **options):
        """
        creates a new measurement as initial state of measurement

        :param mtype: measurement type
        :param mfile:  measurement data file
        :param machine: measurement machine
        :param options:
        :return:
        """
        self.log.info('CREATING << %s >> initial state measurement << %s >> data' % (mtype, self.mtype))
        implemented = {i.__name__.lower(): i for i in Measurement.inheritors()}
        if mtype in implemented_measurements:
            self.initial_state = implemented_measurements[mtype](self.sample_obj, mtype, mfile, machine)
            # self.initial_state = self.initial_state_obj.data
        else:
            self.log.error('UNABLE to find measurement << %s >>' % (mtype))

    def add_treatment(self, ttype, tvalue, comment=''):
        treatment = Generic(ttype=ttype, value=tvalue, comment=comment)
        self.treatments.append(treatment)

    @property
    def generic(self):
        '''
        helper function that returns the value for a given statistical method. If result not available will calculate
        it with standard parameters
        '''
        return self.result_generic()


    def result_generic(self, **parameter):
        '''
        Generic for for result implementation. Every calculation of result should be in the self.results data structure
        before calculation.
        It should then be tested if a value for it exists, and if not it should be created by calling
        _calculate_result_(result_name).

        '''
        # NAMING! no '_' allowed after result
        if self.results['generic'] is None:
            self.calculate_generic(**parameter)
        return self.results['generic']


    def calculate_generic(self, **parameter):
        '''
        actual calculation of the result

        :return:
        '''

        self.results['generic'] = 0

    def calc_generic(self, **parameter):
        '''
        helper function
        actual calculation of the result

        :return:
        '''

        self.results['generic'] = 0

    def calc_result(self, parameter, recalc, force_caller=None):
        '''
        Helper function:
        Calls any calculate_* function, but checks first:
            1. does this calculation method exist
            2. has it been calculated before
               |- NO : calculate the result
               |- YES: are given parameters equal to previous calculation parameters
                  |- NO : calculate result with new parameters
                  |- YES: return previous result
        :param parameter: dict
                        dictionary with parameters needed for calculation
        :param caller: calling function name without calculate_
        :param force_caller: not dynamically retrieved caller name.
        :return:
        '''

        if force_caller is not None:
            caller = force_caller
        else:
            caller = '_'.join(inspect.stack()[1][3].split('_')[1:])

        if callable(getattr(self, 'calculate_' + caller)):  # check if calculation function exists
            parameter = self.compare_parameters(caller, parameter,
                                                recalc)  # checks for None and replaces it with standard
            if self.results[caller] is None or self.results[
                caller] == 0.000 or recalc:  # if results dont exist or force recalc #todo exchange 0.000 with np.nan
                if recalc:
                    self.log.debug('FORCED recalculation of << %s >>' % (caller))
                else:
                    self.log.debug('CANNOT find result << %s >> -> calculating' % (caller))
                getattr(self, 'calculate_' + caller)(**parameter)  # calling calculation method
            else:
                self.log.debug('FOUND previous << %s >> parameters' % (caller))
                if self.check_parameters(caller, parameter):  # are parameters equal to previous parameters
                    self.log.debug('RESULT parameters different from previous calculation -> recalculating')
                    getattr(self, 'calculate_' + caller)(**parameter)  # recalculating if parameters different
                else:
                    self.log.debug('RESULT parameters equal to previous calculation')
        else:
            self.log.error(
                'CALCULATION of << %s >> not possible, probably not implemented, yet.' % caller)

    def calc_all(self, **parameter):
        parameter['recalc'] = True
        for result_method in self.result_methods:
            getattr(self, 'result_' + result_method)(**parameter)

    def compare_parameters(self, caller, parameter, recalc):
        """
        checks if given parameter[key] is None and replaces it with standard parameter or calculation_parameters.

        e.g. calculation_generic(A=1, B=2)
             calculation_generic() # will calculate with A=1, B=2
             calculation_generic(A=3) # will calculate with A=3, B=2
             calculation_generic(A=2, recalc=True) # will calculate with A=2 B=standard_parameter['B']

        :param caller: str
                     name of calling function ('result_generic' should be given as 'generic')
        :param parameter:
                        Parameters to check
        :param recalc: Boolean
                     True if forced recalculation, False if not
        :return:
        """
        # caller = inspect.stack()[1][3].split('_')[-1]

        for i, v in parameter.iteritems():
            if v is None:
                if self.calculation_parameters[caller] and not recalc:
                    parameter[i] = self.calculation_parameters[caller][i]
                else:
                    parameter[i] = self.standard_parameters[caller][i]
        return parameter

    def check_parameters(self, caller, parameter):
        '''
        Checks if previous calculation used the same parameters, if yes returns the previous calculation
        if no calculates with new parameters
        :param caller: str
                     name of calling function ('result_generic' should be given as 'result')
        :param parameter:
        :return:
        '''

        if self.calculation_parameters[caller]:
            a = [parameter[i] for i in self.calculation_parameters[caller]]
            b = [self.calculation_parameters[caller][i] for i in self.calculation_parameters[caller]]
            if a != b:
                return True
            else:
                return False
        else:
            return True


    @classmethod
    def inheritors(cls):
        subclasses = set()
        work = [cls]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses