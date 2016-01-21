from pydub import AudioSegment
import numpy as np


SUFFIXES = {'aif': 'aiff',
            'wave': 'wav'}

def read_audio_file_to_object(fname):
    '''
    '''
    ftype = fname[-3:]
    if ftype in SUFFIXES:
        ftype = SUFFIXES[ftype]
    return AudioSegment.from_file(fname, ftype)


def convolve(a, b):
    '''
    Input:
        two AudioSegment objects.
    Output: 
        two numpy arrays (l & r channels) of the convolved waveform. 
    '''
    samples = [(s.channels % 2 + 1) * s.split_to_mono() for s in [a, b]]
    a, b = [[np.array(c.get_array_of_samples()) for c in s] for s in samples]
    return [np.convolve(a[i], b[i]) for i in (0, 1)]
    

def write_stereo_arrays_to_wav(L_and_R):
    '''
    '''
    strings = [s.tostring() for s in L_and_R]
    audio_objs = []
    for i, s in enumerate(strings):
        text = open('output/%s.output' %('Left', 'Right')[i], 'w')
        text.write(s)
        text.close()
        a = AudioSegment.from_raw('output/%s.output'%('Left', 'Right')[i],
                                  frame_rate=44100, channels=1, sample_width=2)
        audio_objs.append(a)
    audio_objs = [a.pan((-1, 1)[i]) for i, a in enumerate(audio_objs)]
    return audio_objs[0].overlay(audio_objs[1])


def go(fname_a, fname_b):
    a, b = (read_audio_file_to_object(f) for f in (fname_a, fname_b))
    conv = convolve(a, b)
    return write_stereo_arrays_to_wav(conv)
    

    
    



