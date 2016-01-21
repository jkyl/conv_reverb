from pydub import AudioSegment
from scipy.signal import fftconvolve
from scipy.io.wavfile import write
import numpy as np
import sys


SUFFIXES = {'aif': 'aiff',
            'wave': 'wav'}

def read_audio_file_to_obj(fname):
    '''
    Creates an AudioSegment object of the filename. Converts filetype suffix
    if necessary. 
    '''
    ftype = fname[-3:]
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


def convolve(a, b):
    '''
    Computes the FFT convolution between the two arrays, seperately for each 
    stereo channel. This way the spatialiazation of the original audio is 
    preserved in the convolution. Outputs one numpy array of the convolution 
    waveform of a and b, with shape (n_chans, n_samps). 
    '''
    return np.array([fftconvolve(a[i], b[i]) for i in (0, 1)])

    
def write_stereo_arrays_to_wav(stereo_array, output_fname):
    '''
    Normalizes the convolved waveform and swaps the axes to the way the scipy
    writer likes it. Writes as a .wav to the specified filepath. 
    '''
    norm = np.int16(32767 * stereo_array/float(np.max(np.abs(stereo_array))))
    if norm.shape[0] == 2:
        norm = norm.swapaxes(0, 1)
    write(output_fname, 44100, norm)
    

def go(fname_a, fname_b, output_fname):
    '''
    Puts it all together.
    '''
    print('~~~~~~~~~~~~~~~~~~~')
    print('reading in files...')
    a, b = (read_audio_file_to_obj(f) for f in (fname_a, fname_b))
    print('converting to arrays...')
    a, b = (audio_obj_to_arrays(o) for o in (a, b))
    print('convolving...')
    conv = convolve(a, b)
    print('writing to disk...')
    write_stereo_arrays_to_wav(conv, output_fname)
    print('done.')
    print('~~~~~~~~~~~~~~~~~~~')
    

if __name__ == '__main__':
    usage = 'usage: python utils.py <fname_a> <fname_b> <output_fname>'
    args_len = len(sys.argv)
    if args_len == 4:
        a, b, c = sys.argv[1:]
    else:
        print(usage)
        sys.exit(0)
    go(a, b, c)
    



