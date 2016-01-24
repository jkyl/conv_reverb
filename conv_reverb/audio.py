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
            self._mono_array = (self._array[0] + self._array[1])/2.
            self._title = ''.join(fname.split('/')[1:])
        else:
            self._array = None
            self._title = 'Untitled'
        
        
    @property
    def title(self):
        return self._title

    @property
    def array(self):
        return self._array
    
    @property
    def mono_array(self):
        return self._mono_array
    
    def set_title(self, title):
        self._title = title
        
    def set_array(self, array):
        if array.shape[0] == 2:
            self._array = array

    def write_to_wav(self):
        utils.write_stereo_arrays_to_wav(self._array,
                                         ''.join(self._title.split('.')[:-1]))

    def plot_waveform(self):
        utils.plot_waveform(self._array, ''.join(self._title.split('.')[:-1]))

    def plot_fft_spectrum(self, window_size_in_samples):
        spectrum = utils.get_fft(self._mono_array, window_size_in_samples)
        utils.plot_fft(spectrum, ''.join(self._title.split('.')[:-1]))

    def convolve(self, audio_obj):
        conv = array_transforms.convolve(self._array, audio_obj.array)
        rv = Audio()
        rv.set_array(conv)
        rv.set_title(self.title + 'convolved with' + audio_obj.title)
        return rv
        
    def pitchshift(self, amt):
        shift = array_transforms.pitchshift(self._array, amt)
        rv = Audio()
        rv.set_array(shift)
        rv.set_title(self.title + 'pitch shifted %s %'%(amt * 100))
        return rv

    def ringmod(self, freq_hz):
        mod = array_transforms.ringmod(self._array, freq_hz)
        rv = Audio()
        rv.set_array(mod)
        rv.set_title(self.title + 'ring modulated at %s Hz'%(freq_hz))
        return rv
