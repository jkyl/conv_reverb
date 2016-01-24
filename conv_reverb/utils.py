from pydub import AudioSegment
from scipy.io.wavfile import write
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import interp2d
import matplotlib.pyplot as plt
import numpy as np
import sys


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
    '''
    x_in_secs = np.arange(len(a[0]))/44100.
    plt.close('all')
    fig, (ax1, ax2) = plt.subplots(2, sharex=True, sharey=True)
    fig.subplots_adjust(left=0.05, bottom=0.08, right=0.98, top=0.92)
    plt.suptitle('"'+title+'"', style='italic')
    ax1.step(x_in_secs, a[0], linewidth = 0.2, color = 'darkmagenta')
    ax1.set_title('Left', loc = 'left')
    ax1.set_xlim([0, x_in_secs[-1]])
    ax1.axes.get_yaxis().set_visible(False)
    ax2.step(x_in_secs, a[1], linewidth = 0.2, color = 'darkmagenta')
    ax2.set_title('Right', loc = 'left')
    ax1.set_xlim([0, x_in_secs[-1]])
    ax2.axes.get_yaxis().set_visible(False)
    plt.xlabel('Seconds')
    plt.xticks(np.arange(0, round(x_in_secs[-1]), round(x_in_secs[-1]/10.)))
    plt.savefig('output/waveforms/' + title)
    
    
    
def write_stereo_arrays_to_wav(stereo_array, title):
    '''
    Normalizes the convolved waveform and swaps the axes to the way the scipy
    writer likes it. Writes as a .wav to the specified filepath. 
    '''
    norm = np.int16(32767 * stereo_array/float(np.max(np.abs(stereo_array))))
    if norm.shape[0] == 2:
        norm = norm.swapaxes(0, 1)
    write('output/wavfiles/' + title, 44100, norm)


def get_fft(a, step_size):
    '''
    '''
    trunc_a = a[:(len(a) - (len(a) % step_size))]
    split_into_steps = np.array_split(trunc_a, len(a) / step_size)
    fourier_coeffs = [np.fft.fft(s) for s in split_into_steps]
    windows = np.array([[np.abs(coeff) for coeff in window[:len(window)/2]] \
                        for window in fourier_coeffs])
    spectrum = windows/windows.max()
    spectrum[np.where(spectrum < .0000009)] = .0000009  # apply noise floor to 
    return 10*np.log10(spectrum.swapaxes(0,1))          # -inf points.    



def plot_fft(spectrum, title):
    '''
    '''
    n_freq_bins, n_time_windows = spectrum.shape
    x_axis = np.linspace(0, n_freq_bins*n_time_windows/44100., n_time_windows)
    y_axis = np.linspace(0, 22050, n_freq_bins)
    interpolation =interp2d(x_axis, y_axis, spectrum, kind = 'cubic')
    new_x = np.linspace(0, x_axis.max(), 500)
    new_y = np.linspace(0, y_axis.max(), 5000)
    spectrum = interpolation(new_x, new_y)
    spectrum = spectrum - spectrum.max()
    X, Y = np.meshgrid(new_x, new_y)
    
    plt.close('all')
    ax = plt.gca()
    im = ax.pcolormesh(X, Y, spectrum, cmap = 'afmhot')
    plt.title(title)
    plt.xlim(0, x_axis.max())
    plt.yscale('log')
    plt.ylim([22.05, 22050])
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency (Hz)')
    plt.tick_params(axis='y', which='minor')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax, ticks = np.arange(0, -70, -10),
                 label = 'Amplitude (dB)')
    plt.savefig('output/spectra/' + title + '.png')
    
    



