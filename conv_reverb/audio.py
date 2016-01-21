import utils
import array_transforms

class Audio:
    '''
    While it is possible to initialize an Audio object without pointing it
    to a file, do not do this! It's only possible so that the transformation
    functions can return other Audio objects and set their arrays without 
    creating segments. 
    '''
    def __init__(self, fname = None):
        if not fname is None:
            self._segment = utils.read_audio_file_to_obj(fname)
            self._array = utils.audio_obj_to_arrays(self._segment)
            self._title = fname.split('.')[0]
        else:
            self._array = None
        
        
    @property
    def title(self):
        return self._title

    @property
    def array(self):
        return self._array

    def set_array(self, array):
        if array.shape[0] == 2:
            self._array = array

    def write_to_wav(self, fname):
        utils.write_stereo_arrays_to_wav(self._array, fname)

    def plot_waveform(self, output_fname = None):
        utils.plot_waveform(self._array, self._title, output_fname)

    def convolve(self, audio_obj):
        conv = array_transforms.convolve(self._array, audio_obj.array)
        rv = Audio()
        rv.set_array(conv)
        return rv
        
    def pitchshift(self, amt):
        shift = array_transforms.pitchshift(self._array, amt)
        rv = Audio()
        rv.set_array(shift)
        return rv

    def ringmod(self, freq_hz):
        mod = array_transforms.ringmod(self._array, freq_hz)
        rv = Audio()
        rv.set_array(mod)
        return rv
