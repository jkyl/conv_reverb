from pydub import AudioSegment
from scipy.signal import fftconvolve
from scipy.io.wavfile import write
import numpy as np
import sys


SUFFIXES = {'aif': 'aiff',
            'wave': 'wav'}

def read_audio_file_to_object(fname):
    '''
    Creates an AudioSegment object of the filename. Converts filetype suffix
    if necessary. 
    '''
    ftype = fname[-3:]
    if ftype in SUFFIXES:
        ftype = SUFFIXES[ftype]
    return AudioSegment.from_file(fname, ftype)


def convolve(a, b):
    '''
    For each input object: if the audio is stereo, splits the object in two, 
    one for each stereo channel. Then loads the raw sample data into numpy 
    arrays. Finally, computes the FFT convolution of the two samples seperately
    for each stereo channel. This way the spatialiazation of the original audio
    is preserved in the convolution. 

    Input:
        Two AudioSegment objects.
    Output: 
        A numpy array of the convolved waveform with shape (n_chans, n_samps). 
    '''
    samples = [(s.channels % 2 + 1) * s.split_to_mono() for s in (a, b)]
    a, b = [[np.array(c.get_array_of_samples()) for c in s] for s in samples]
    return np.array([fftconvolve(a[i], b[i]) for i in (0, 1)])

    
def write_stereo_arrays_to_wav(stereo, output_fname):
    '''
    Normalizes the convolved waveform and swaps the axes to the way the scipy
    writer likes it. Writes as a .wav to the specified filepath. 
    '''
    norm = np.int16(32767 * stereo/float(np.max(np.abs(stereo))))
    if norm.shape[0] == 2:
        norm = norm.swapaxes(0, 1)
    write(output_fname, 44100, norm)
    

def go(fname_a, fname_b, output_fname):
    '''
    Puts it all together.
    '''
    print('~~~~~~~~~~~~~~~~~~~')
    print('reading in files...')
    a, b = (read_audio_file_to_object(f) for f in (fname_a, fname_b))
    print('convolving...')
    conv = convolve(a, b)
    print('writing to disk...')
    write_stereo_arrays_to_wav(conv, output_fname)
    print('done.')
    print('~~~~~~~~~~~~~~~~~~~')
    

if __name__ == '__main__':
    usage = 'python utils.py <fname_a> <fname_b> <output_fname>'
    args_len = len(sys.argv)
    if args_len == 4:
        a, b, c = sys.argv[1:]
    else:
        print(usage)
        sys.exit(0)
    go(a, b, c)
    



