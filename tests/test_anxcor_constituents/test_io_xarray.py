import unittest
from obsplus.bank import WaveBank
from obspy.core import Stream, Trace
from os_utils import _clean_files_in_dir, _how_many_fmt
from anxcor.anxcor_main import Anxcor
from anxcor.xarray_routines import XArrayTemporalNorm, XArrayWhiten
import numpy as np
import xarray as xr

source_dir = '../test_data/test_ancor_bank/test_waveforms_multi_station'
target_dir = '../test_data/test_ancor_bank/test_save_output'

starttime_stamp = 1481761092.0 + 3600 * 24


class TestProcess:

    def __init__(self):
        pass

    def process(self, trace):
        pass


def get_ancor_set():
    bank = WaveBank(source_dir)
    return bank


class WavebankWrapper:

    def __init__(self, directory):
        self.bank = WaveBank(directory)
        import warnings
        warnings.filterwarnings("ignore")

    def get_waveforms(self, **kwargs):
        stream =  self.bank.get_waveforms(**kwargs)
        traces = []
        for trace in stream:
            data = trace.data[:-1]
            header = {'delta':np.floor(trace.stats.delta*1000)/1000.0,
                      'station': trace.stats.station,
                      'starttime':trace.stats.starttime,
                      'channel': trace.stats.channel,
                      'network': trace.stats.network}
            traces.append(Trace(data,header=header))
        return Stream(traces=traces)

    def get_stations(self):
        df = self.bank.get_uptime_df()

        def create_seed(row):
            network = row['network']
            station = row['station']
            return network + '.' + station

        df['seed'] = df.apply(lambda row: create_seed(row), axis=1)
        unique_stations = df['seed'].unique().tolist()
        return unique_stations


class TestIntegratedIOOps(unittest.TestCase):


    def test_single_execution(self):
        # stations 21, & 22
        # 3 windows say
        #
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)

        self.assertTrue(isinstance(result, xr.Dataset))


    def test_read_xconvert(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='xconvert')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.read_from_file_at_step(target_dir, type='xconvert')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        _clean_files_in_dir(target_dir)
        self.assertTrue(isinstance(result,xr.Dataset))

    def test_write_xconvert(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='xconvert')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(8, how_many_nc)

    def test_write_resample(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='resample')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(8, how_many_nc)

    def test_read_resample(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='resample')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.read_from_file_at_step(target_dir, type='resample')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(8, how_many_nc)

    def test_write_correlate(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='correlate')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(12, how_many_nc)

    def test_read_correlate(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='correlate')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.read_from_file_at_step(target_dir, type='correlate')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(12, how_many_nc)

    def test_write_stack(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='stack')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(9, how_many_nc)

    def test_read_stack(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='stack')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.read_from_file_at_step(target_dir, type='stack')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(9, how_many_nc)

    def test_write_combine(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate',dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='combine')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(2, how_many_nc)

    def test_read_combine(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.write_result_to_file(target_dir, type='combine')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate',dict(dummy_task=True))
        anxcor.read_from_file_at_step(target_dir, type='combine')
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(2, how_many_nc)

    def test_write_tempnorm(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.add_process(XArrayTemporalNorm(time_mean=5.0,lower_frequency=0.02))
        anxcor.write_result_to_file(target_dir,type='process',order=0)
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(8, how_many_nc)

    def test_read_tempnorm(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.add_process(XArrayTemporalNorm(time_mean=5.0, lower_frequency=0.02))
        anxcor.write_result_to_file(target_dir, type='process', order=0)
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.add_process(XArrayTemporalNorm(time_mean=5.0,lower_frequency=0.02))
        anxcor.read_from_file_at_step(target_dir,type='process',order=0)
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(8, how_many_nc)

    def test_write_whitening(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.add_process(XArrayWhiten())
        anxcor.write_result_to_file(target_dir,type='process',order=0)
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(8, how_many_nc)


    def test_read_whitening(self):
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.add_process(XArrayWhiten())
        anxcor.write_result_to_file(target_dir,type='process',order=0)
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        anxcor = Anxcor(3600, 0.5)
        bank = WavebankWrapper(source_dir)
        anxcor.add_dataset(bank, 'nodals')
        anxcor.set_parameters('correlate', dict(dummy_task=True))
        anxcor.add_process(XArrayWhiten())
        anxcor.read_from_file_at_step(target_dir, type='process', order=0)
        result = anxcor.process(starttime=starttime_stamp, endtime=starttime_stamp + 2 * 3600)
        how_many_nc = _how_many_fmt(target_dir, format='.nc')
        _clean_files_in_dir(target_dir)
        self.assertEqual(8, how_many_nc)


if __name__ == '__main__':
    unittest.main()