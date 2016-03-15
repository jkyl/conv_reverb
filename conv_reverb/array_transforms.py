import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import fftconvolve

def convolve(a, b):
    '''
    Computes the Fast Fourier Transform convolution between two arrays, seperately for each 
    stereo channel. This way the spatialiazation of the original audio is 
    preserved in the convolution. Outputs one numpy array of the convolution 
    waveform of a and b, with shape (n_chans, n_samps). 
    '''
    return np.array([fftconvolve(a[i], b[i]) for i in (0, 1)])

def correlate(a, b):
    '''
    Computes the FFT correlation between two MONO arrays (convolution of one by 
    the reverse of the other).
    '''
    return fftconvolve(a, b[::-1])


def pitchshift(a, scale):
    '''
    Waveform a is pitchshifted up or down by scale, where 0 < scale < inf.
    Works by creating an interpolation, stretching its x-axis and then 
    populating the interpolation at the native sample rate. 
    '''
    fxns = (interp1d(np.linspace(0, (len(chan) / float(scale)), len(chan)),
                     chan) for chan in a)
    return np.array([f(np.arange(len(a[i]) / float(scale))) \
                     for i, f in enumerate(fxns)])


def ringmod(a, freq_hz):
    '''
    Waveform a is ring modulated with a sine signal with frequency freq_hz. 
    This amounts to multiplying the two signals together. 
    '''
    freq_samps = freq_hz / 44100.
    return np.array([np.multiply(chan, np.sin(np.arange(len(chan)) * freq_samps\
                                 )) for chan in a])

def delay(a, time, dry_wet, feedback):
    '''
    '''
    assert(feedback <= 0.95)
    d = np.array([1.])
    next_d = np.zeros(time * 44100.)
    next_d[-1] = 1
    d = np.concatenate((d, next_d))  
    while (d[-1] * dry_wet) > 0.01:
        next_d = np.zeros(time * 44100.)
        next_d[-1] = d[-1] * feedback
        d = np.concatenate((d, next_d))              
    d[1:] = d[1:] * dry_wet
    d = np.array([d, d])
    return convolve(a, d)
                           
    
