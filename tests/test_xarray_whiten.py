import unittest

from anxcor import anxcor_utils
from anxcor.xarray_routines import XArrayWhiten, XArrayConverter, XArrayResample, XArrayRemoveMeanTrend
# for travis build
try:
    from tests.synthetic_trace_factory import  create_sinsoidal_trace
except:
    from synthetic_trace_factory import  create_sinsoidal_trace

from scipy.signal import correlate
from obspy.clients.fdsn import Client
import pytest
from obspy.core import UTCDateTime, Stream
import numpy as np
import anxcor.filters as filts
whiten = XArrayWhiten(window=0.1, freqmax=20.0, freqmin=0.001,
                      order=2, rolling_metric='mean')
convert = XArrayConverter()

def plot_spectrum(xarray):
    import matplotlib.pyplot as plt
    freq_array = filts.xarray_time_2_freq(xarray)
    plt.figure()
    abs(freq_array.squeeze()).plot.line(x='frequency',xscale='log',
                                        yscale='log')
    plt.show()

class TestSpectralWhitening(unittest.TestCase):

    def test_whitened_success(self):

        trace    = convert(create_sinsoidal_trace(sampling_rate=100,period=0.5,    duration=3))
        freq_2   = convert(create_sinsoidal_trace(sampling_rate=100, period=0.1,   duration=3))
        target_trace       = trace +  freq_2
        target_trace.attrs = freq_2.attrs
        target             = self.get_power_at_freq(6.0,target_trace)
        source_trace       = whiten(target_trace,starttime=0,station=0)
        source             = self.get_power_at_freq(6.0, source_trace)
        assert target < source,"whitening failed"

    def test_array_is_real(self):
        tr_1 = create_sinsoidal_trace(sampling_rate=100, period=0.5, duration=3)
        tr_2 = create_sinsoidal_trace(sampling_rate=100, period=0.1, duration=3)
        st1 = Stream(traces=[*tr_1,*tr_2])
        st2 = Stream(traces=[*tr_2, *tr_2])
        trace = convert(st1)
        freq_2 = convert(st2)
        trace = trace + freq_2
        trace.attrs = freq_2.attrs
        trace = whiten(trace)

        assert trace.data.dtype == np.float64,'improper data type'


    def get_power_at_freq(self, frequency, xarray):
        data         = xarray.data.ravel()
        delta        = xarray.attrs['delta']
        fft_spec     = filts._into_frequency_domain(data)
        fft_spec    /= max(abs(fft_spec))
        frequencies  = filts._get_deltaf(data.shape[-1], delta)
        index_val    = self.find_nearest(frequencies,frequency)

        value_at_freq = fft_spec[index_val]

        power_at_freq = np.abs(value_at_freq * np.conjugate(value_at_freq))

        return power_at_freq

    def find_nearest(self,array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

    def test_nonetype_in_out(self):
        result = whiten(None,starttime=0,station=0)
        assert True

    def test_jupyter_tutorial_tapers(self):
        client = Client("IRIS")
        t = UTCDateTime("2018-12-25 12:00:00").timestamp
        st = client.get_waveforms("UU", "SPU", "*", "H*", t, t + 10 * 60, attach_response=True)
        pre_filt = (0.01, 0.03, 40.0, 45.0)
        st = anxcor_utils.remove_response(st, output='DISP', pre_filt=pre_filt,
                                                    zero_mean=True, taper=True)
        converter = XArrayConverter()
        resampler = XArrayResample(target_rate=10.0)
        rmmean_trend = XArrayRemoveMeanTrend()

        xarray = converter(st)
        resampled_array = resampler(xarray)
        rmm_array = rmmean_trend(resampled_array)
        whitening_op = XArrayWhiten(taper=0.05, whiten_type='cross_component', freqmax=3.0,
                                    freqmin=0.01, smoothing_window_ratio=0.01)

        whitened_array = whitening_op(rmm_array)
        assert whitened_array.data[0,0,0]==pytest.approx(0,abs=1e-2)


    def test_phase_shift(self):
        stream   = create_sinsoidal_trace(sampling_rate=40.0, duration = 1000.0,
                                                               period=20)

        stream[0].data+=np.random.uniform(-0.01,0.01,stream[0].data.shape)
        converter = XArrayConverter()
        xarray = converter(stream)
        taper=0.1
        center=False
        ratio = 0.01
        whitening_op = XArrayWhiten(taper=0.1, window=0.05, whiten_type='cross_component', freqmax=20.0,
                                    freqmin=0.01, center=center, order=2)

        whitened_array = whitening_op(xarray)
        a = whitened_array.data[0,0,:].squeeze()
        b = xarray.data[0,0,:].squeeze()
        xcorr = correlate(a, b)

        # delta time array to match xcorr
        dt = np.arange(1 - a.shape[-1], a.shape[-1])

        recovered_time_shift = dt[xcorr.argmax()]

        assert recovered_time_shift==0

    def test_symmetric_output(self):
        converter = XArrayConverter()
        signal_length = 1000
        sampling_rate = 20.0
        center_index = int(signal_length * sampling_rate) // 2
        stream = create_sinsoidal_trace(sampling_rate=sampling_rate, duration=signal_length,
                                        period=2)
        stream1 = create_sinsoidal_trace(sampling_rate=sampling_rate, duration=signal_length,
                                         period=0.5)
        stream[0].data += stream1[0].data

        stream[0].data += np.random.uniform(-0.01, 0.01, stream[0].data.shape)
        converter = XArrayConverter()
        xarray = converter(stream)
        center = True
        whitening_op = XArrayWhiten(taper=0.1, window=0.05, whiten_type='cross_component', freqmax=20.0,
                                    freqmin=0.01, center=center, order=2)
        whitened_array = whitening_op(xarray)
        xarray_squeezed = whitened_array[0, 0, :].data.squeeze()
        difference  = xarray_squeezed[:center_index]- xarray_squeezed[-center_index:]
        cumdiff     = abs(np.cumsum(difference)[-1]/(signal_length*sampling_rate))
        assert pytest.approx(0,abs=1e-4)==cumdiff

if __name__ == '__main__':
    unittest.main()