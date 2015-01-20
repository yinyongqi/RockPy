__author__ = 'volk'
import os
from os.path import join
import RockPy

def get_hys_all_sample():
    folder = RockPy.test_data_path
    S = RockPy.Sample(name='test_sample',
                                 mass=14.2, mass_unit='mg',
                                 diameter=5.4, length_unit='nm',
                                 height=23.8)

    mfile1 = join(folder, 'MUCVSM_test.hys')
    mfile2 = join(folder, 'MUCVFTB_test.hys')
    S.add_measurement(mtype='hysteresis', mfile=mfile1, machine='vsm')
    S.add_measurement(mtype='hysteresis', mfile=mfile2, machine='vftb')
    return S


def get_hys_coe_irm_rmp_sample():
    # folder = os.getcwd().split('RockPy')[0]
    folder = RockPy.test_data_path
    S = RockPy.Sample(name='test_sample')
    hys = join(folder, 'MUCVFTB_test.hys')
    coe = join(folder, 'MUCVFTB_test.coe')
    irm = join(folder, 'MUCVFTB_test.irm')
    rmp = join(folder, 'MUCVFTB_test.rmp')
    S.add_measurement(mtype='hysteresis', mfile=hys, machine='vftb', treatments='temp, 20, C; pressure, 1, GPa')
    S.add_measurement(mtype='hysteresis', mfile=hys, machine='vftb', treatments='temp, 20, C')
    S.add_measurement(mtype='backfield', mfile=coe, machine='vftb')
    S.add_measurement(mtype='irm_acquisition', mfile=irm, machine='vftb')
    S.add_measurement(mtype='thermocurve', mfile=rmp, machine='vftb')
    return S

def get_af_demag_sample():
    folder = RockPy.test_data_path
    S = RockPy.Sample(name='WURM')
    af = join(folder, 'MUCSUSH_af_test.af')
    S.add_measurement(mtype='afdemag', mfile=af, machine='sushibar', magtype='irm')
    return S

def get_pmd_demag():
    S = RockPy.Sample(name='test_sample')
    dm = 'RockPy/Tutorials/test_data/HA2A.pmd'
    S.add_measurement(mtype='afdemag', mfile=dm, machine='pmd')
    return S

def test():
    S = get_pmd_demag()
    study = RockPy.Study("study", samplegroups=S)
    RockPy.save(study, 'hys_coe_irm_rmp.rpy')
    #print S.plottable
    #print study.all_samplegroup.mtypes

if __name__ == '__main__':
    test()