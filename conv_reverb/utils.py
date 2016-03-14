from pydub import AudioSegment
from scipy.io.wavfile import write
from scipy.interpolate import interp2d
from scipy.fftpack import fft
from scipy.signal import blackman
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy as np
import sys
import math


SUFFIXES = {'aif': 'aiff',
            'wave': 'wav'}

def read_audio_file_to_obj(fname):
    '''
    Creates an AudioSegment object of the filename. Converts filetype suffix
    if necessary. 
    '''
    ftype = fname.split('.')[-1]
    if ftype in SUFFIXES:
        ftype = SUFFIXES[ftype]
    return AudioSegment.from_file(fname, ftype)


def audio_obj_to_arrays(obj):
    '''
    Accepts an AudioSegment object and converts to a raw format (16-bit 
    integers in numpy arrays). If the audio is stereo, splits the object into
    two objects, one for each stereo channel, then loads the sample data into 
    numpy arrays.
    '''
    split = (obj.channels % 2 + 1) * obj.split_to_mono()
    return np.array([s.get_array_of_samples() for s in split])


def plot_waveform(a, title):
    '''
    Plots the stereo arrays in purple. Saves as output/waveforms/title/.png
    '''
    x_in_secs = np.arange(len(a[0]))/44100.
    plt.close('all')
    fig, (ax1, ax2) = plt.subplots(2, sharex=True, sharey=True)
    fig.subplots_adjust(left=0.05, bottom=0.08, right=0.98, top=0.92)
    plt.suptitle('"'+title+'"', style='italic')
    ax1.step(x_in_secs, a[0], linewidth = 0.2, color = 'darkmagenta')
    ax1.set_title('Left', loc = 'left')
    ax1.set_xlim([0, x_in_secs[-1]])
    ax1.set_ylim([a[0].min() * 0.95, a[0].max() * 1.05])
    ax1.axes.get_yaxis().set_visible(False)
    ax2.step(x_in_secs, a[1], linewidth = 0.2, color = 'darkmagenta')
    ax2.set_title('Right', loc = 'left')
    ax2.set_ylim([a[1].min() * 0.95, a[1].max() * 1.05])
    ax2.axes.get_yaxis().set_visible(False)
    plt.xlabel('Seconds')
    #plt.xticks(np.arange(0, round(x_in_secs[-1]), round(x_in_secs[-1]/10.)))
    plt.savefig('' + title)
    
    
    
def write_stereo_arrays_to_wav(stereo_array, title):
    '''
    Normalizes the convolved waveform and swaps the axes to the way the scipy
    writer likes it. Writes as a .wav to the specified filepath. 
    '''
    norm = np.int16(32767 * stereo_array/float(np.max(np.abs(stereo_array))))
    if norm.shape[0] == 2:
        norm = norm.swapaxes(0, 1)
    write('output/wavfiles/' + title +'.wav', 44100, norm)


def get_fft(a, step_size):
    '''
    Zero-pads an array so that its a multiple of step_size. Splits it into
    two sets of step_size'd windows - an "outer" and "inner". These two sets
    overlap by step_size/2. Interleaves the two sets and applies a blackman
    (cosine) envelope to each window. Takes the fft of each window and takes 
    the fourier coefficients times their complex conjugate to get the power 
    spectrum for each window. Applies a noise floor of -130dB to account for
    the case where the magnitude of the fourier coefficient is zero (-inf on 
    a log scale which we cannot plot). We chose -130dB because if 0dB causes
    your ears to bleed, -130dB would be the quietest thing you could possibly 
    hear. Then we take the log base 10 and swap the axes to be plt.imshow()
    -able. 
    '''
    pad = step_size - (a.size % step_size)
    zerod = np.append(a, np.zeros(pad))
    outer = zerod.reshape(zerod.size / step_size, step_size)
    inner = zerod[(step_size / 2):(-step_size / 2)]\
            .reshape((zerod.size - step_size) / step_size, step_size)
    interleaved = np.empty([outer.shape[0] + inner.shape[0], outer.shape[1]])
    interleaved[::2,:] = outer; interleaved[1::2,:] = inner
    windowed = blackman(step_size) * interleaved
    coeffs = fft(windowed)[:, :(step_size / 2) + 1]
    power_units = np.abs(np.multiply(coeffs, np.conj(coeffs)))
    power_units = power_units/power_units.max()
    power_units[np.where(power_units < 1e-13)] = 1e-13
    decibels = 10 * np.log10(power_units)
    
    return decibels.swapaxes(0, 1)
    

def plot_fft(spectrum, title):
    '''
    Plots a spectrogram as obtained in the above function. These conventions
    are mostly lifted straight from the matplotlib api. It's important that 
    you have matplotlib 5.1 though in order to use the 'inferno' colormap. 
    '''
    n_bins, n_windows = spectrum.shape
    x_axis = np.linspace(0, (n_bins - 1) * n_windows / 44100., n_windows)
    y_axis = np.linspace(0, 22050., n_bins)
    X, Y = np.meshgrid(x_axis, y_axis)
    #plt.close('all')
    ax = plt.gca()
    ax.set_yscale('symlog')
    im = ax.pcolormesh(X, Y, spectrum, cmap = 'gist_heat')
    plt.title(title)
    plt.xlim(0, x_axis.max())
    plt.ylim(y_axis[1], 22050)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency (Hz)')
    plt.tick_params(axis='y', which='minor')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax, ticks = np.arange(0, -140, -20),
                 label = 'Power (dB)')
    plt.savefig('output/spectra/' + title + '.png')

