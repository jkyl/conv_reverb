import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import fftconvolve

def convolve(a, b):
    '''
    Computes the FFT convolution between two arrays, seperately for each 
    stereo channel. This way the spatialiazation of the original audio is 
    preserved in the convolution. Outputs one numpy array of the convolution 
    waveform of a and b, with shape (n_chans, n_samps). 
    '''
    return np.array([fftconvolve(a[i], b[i]) for i in (0, 1)])


def pitchshift(a, scale):
    '''
    '''
    fxns = (interp1d(np.linspace(0, (len(chan) / float(scale)), len(chan)),
                     chan) for chan in a)
    return np.array([f(np.arange(len(a[i]) / float(scale))) \
                     for i, f in enumerate(fxns)])


def ringmod(a, freq_hz):
    '''
    '''
    freq_samps = freq_hz / 44100.
    return np.array([np.multiply(chan, np.sin(np.arange(len(chan)) * freq_samps\
                                 )) for chan in a])
