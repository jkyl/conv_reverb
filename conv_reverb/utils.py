from pydub import AudioSegment
from scipy.io.wavfile import write
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
    ftype = fname.split('.')[1]
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


def plot_waveform(a, title, output_fname = None):
    '''
    '''
    plt.clf()
    x_in_secs = np.arange(len(a[0]))/44100.
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
    plt.show()
    if not output_fname is None:
        plt.savefig(output_fname)
    
    
    
def write_stereo_arrays_to_wav(stereo_array, output_fname):
    '''
    Normalizes the convolved waveform and swaps the axes to the way the scipy
    writer likes it. Writes as a .wav to the specified filepath. 
    '''
    norm = np.int16(32767 * stereo_array/float(np.max(np.abs(stereo_array))))
    if norm.shape[0] == 2:
        norm = norm.swapaxes(0, 1)
    write(output_fname, 44100, norm)
    
    



