

__author__ = 'mike'
import inspect
import numpy as np
import base
import RockPy.Functions.general
import RockPy.Measurements.hysteresis
import RockPy.Measurements.backfield
import RockPy.PlottingOLD.hysteresis
import RockPy.PlottingOLD.backfield
import RockPy.PlottingOLD.day_plot
from RockPy.Visualize.Features.day import day_grid
from Features import day


class Day1977(base.Generic):
    _required = ['hysteresis', 'backfield']

    def initialize_visual(self):
        # super(Day1977, self).initialize_visual()
        self.standard_features = [day.points]
        self.single_features = [self.feature_day_grid]
        self.add_plot()
        self.ax = self.figs[self.name][0].gca()

        self.ax.set_xlim([0, 8])
        self.ax.set_ylim([0, 0.6])
        self.xlabel = '$B_{cr} / B_c$'
        self.ylabel = '$M_{rs} / M_{s}$'

    def plotting(self, samples, **plt_opt):
        samples = self.get_plot_samples()
        for sample in samples:
            hys = sample.get_measurements(mtypes='hysteresis')[0]
            coe = sample.get_measurements(mtypes='backfield')[0]
            hys.calc_all()
            coe.calc_all()
            mrs_ms = hys.results['mrs'].v / hys.results['ms'].v
            bcr_bc = coe.results['bcr'].v / hys.results['bc'].v
            self.ax.plot(bcr_bc, mrs_ms, '.')

        for feature in self.single_features:
            feature()


    ''' PLOT FEATURES '''
    def feature_points(self):
        pass

    def feature_sd_md1(self, **plt_opt):
        lines, texts = day.sd_md_mixline_1(self.ax, **plt_opt)
        self._add_line_text_dict(lines, texts)

    def feature_sd_md2(self, **plt_opt):
        lines, texts = day.sd_md_mixline_2(self.ax, **plt_opt)
        self._add_line_text_dict(lines, texts)

    def feature_langevin(self, **plt_opt):
        lines, texts = day.langevine_mixline(self.ax, **plt_opt)
        self._add_line_text_dict(lines, texts)

    def feature_sd_sp_10nm(self, **plt_opt):
        lines, texts = day.sd_sp_10nm(self.ax, **plt_opt)
        self._add_line_text_dict(lines, texts)

    def feature_sd_sp_15nm(self, **plt_opt):
        lines, texts = day.sd_sp_15nm(self.ax, **plt_opt)
        self._add_line_text_dict(lines, texts)

    def feature_sp_envelope(self, **plt_opt):
        lines, texts = day.sp_envelope(self.ax, **plt_opt)
        self._add_line_text_dict(lines, texts)


    def feature_day_grid(self, **plt_opt):
        lines, texts = day.day_grid(self.ax, **plt_opt)
        self._add_line_text_dict(lines, texts)

    def feature_data(self):
        print self.get_required_measurements()


class Fabian2010(base.Generic):
    _required = ['hysteresis', 'backfield']

    def initialize_visual(self):
        super(Fabian2010, self).initialize_visual()
        self.add_plot()
        self.ax = self.figs['fabian2010'][0].gca()
        self.ax.set_xlabel('Field [T]')
        self.ax.set_ylabel('Moment [$Am2$]')
        self.ax.ticklabel_format(axis='both', style='sci', scilimits=(-2, 2))

    def plotting(self, sample):
        hys = sample.get_measurements(mtypes='hysteresis')[0]
        coe = sample.get_measurements(mtypes='backfield')[0]

        p_cor = self.options.get('paramag_correct', False)

        if p_cor:
            hys.simple_paramag_cor()

        RockPy.PlottingOLD.hysteresis.zero_lines(self.ax, color='k')
        RockPy.PlottingOLD.hysteresis.up_field_branch(self.ax, hysteresis_obj=hys, color='k')
        RockPy.PlottingOLD.hysteresis.down_field_branch(self.ax, hysteresis_obj=hys, color='k')
        RockPy.PlottingOLD.hysteresis.vigin_branch(self.ax, hysteresis_obj=hys, color='k')
        # RockPy.PlottingOLD.hysteresis.hys_text(self.ax, hysteresis_obj=hys) #todo
        RockPy.PlottingOLD.backfield.backfield(self.ax, coe, color='k')

