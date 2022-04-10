# need to install librtlsdr

from rtlsdr import RtlSdr

print('sdr')
sdr = RtlSdr()
print('config')
# configure device
sdr.sample_rate = 2.048e6  # Hz
sdr.center_freq = 70e6     # Hz
sdr.freq_correction = 60   # PPM
sdr.gain = 'auto'

print(sdr.read_samples(512))