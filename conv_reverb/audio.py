import utils
import array_transforms
import numpy as np

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
            self._title = fname.split('/')[-1].split('.')[0]
        else:
            self._array = None
            self._title = 'Untitled'
        
        
    @property
    def title(self):
        '''
        Getter for title.
        '''
        return self._title

    @property
    def array(self):
        '''
        Getter for stereo arrays.
        '''
        return self._array
    
    @property
    def mono_array(self):
        '''
        Getter for mono array.
        '''
        return (self._array[0] + self._array[1])/2.
    
    def _set_title(self, title):
        '''
        Hidden setter for title.
        '''
        self._title = title
        
    def _set_array(self, array):
        '''
        Hidden setter for stereo array.
        '''
        if array.shape[0] == 2:
            self._array = array

    def write_to_wav(self):
        '''
        Calls the utility to write the stereo arrays to a stereo .wav file
        at output/wavfiles/[self.title].wav
        '''
        utils.write_stereo_arrays_to_wav(self._array, self._title)

    def plot_waveform(self):
        '''
        Plots the time-series data for left and right stereo channels. Does
        not show by default - just saves to output/waveforms/[self.title].png
        '''
        utils.plot_waveform(self._array, self._title)

    def get_fft(self, window_size_in_samples = 512):
        '''
        Calls the utility to get a spectrogram (2d array of power spectrum
        over time) with the specified buffer size (default 512). 
        '''
        return utils.get_fft(self.mono_array, window_size_in_samples)
        
    def plot_fft_spectrum(self, window_size_in_samples = 512):
        '''
        Calls the utility to plot the spectrogram with a beautiful MPL5
        colormap. 
        '''
        spectrum = self.get_fft(window_size_in_samples)
        utils.plot_fft(spectrum, self._title)

    def convolve(self, audio_obj):
        '''
        Returns a new audio object whose array is the convolution between
        this one and another one. Sets its title too. 
        '''
        conv = array_transforms.convolve(self._array, audio_obj.array)
        rv = Audio()
        rv._set_array(conv)
        rv._set_title(self.title + ' convolved with ' + audio_obj.title)
        return rv
        
    def pitchshift(self, amt):
        '''
        Calls the pitchshift transformation on the stereo arrays and returns
        a new audio object and sets its title, as above. 
        '''
        shift = array_transforms.pitchshift(self._array, amt)
        rv = Audio()
        rv._set_array(shift)
        rv._set_title(self.title + ' pitch shifted {}%'.format(int(amt * 100)))
        return rv

    def ringmod(self, freq_hz):
        '''
        Calls the ringmod tranform on the stereo arrays and returns a new audio
        object and sets its title. 
        '''
        mod = array_transforms.ringmod(self._array, freq_hz)
        rv = Audio()
        rv._set_array(mod)
        rv._set_title(self.title + ' ring modulated at {} Hz '.format(int(freq_hz)))
        return rv

    def correlate(self, l):
        '''
        Takes a list or tuple of audio objects and returns a dictionary of their
        ranking wrt. how well they correlate with this object. Performs the 
        correlation only on mono arrays, normalized to have the same power 
        (defined here as magnitude of amplitude per unit time). The arrays are 
        also mean-subtracted and set to std of 1. The correlation winner is 
        determined as the one with the maximum total power of its correlation 
        with this object. The logic is that we need to choose the winner by the
        same metric that we equalize the competitors - that way no one has an
        advantage by having intrinsically higher power. 
        '''
        a = self.mono_array
        rms = ((a**2).sum()/a.size)**.5
        a = a / rms
        a = a - a.mean()
        a = a / a.std()
        if not type(l) in (list, tuple):
            l = [l]
            
        c = []; d = {}
        for i, e in enumerate(l):
            r = e.mono_array
            rms = ((r**2).sum()/r.size)**.5          
            r = r / rms
            r = r - r.mean()
            r = r / r.std()
            c.append(array_transforms.correlate(a, r))
            rms = ((c[i]**2).sum()/c[i].size)**.5
            d[e.title] = rms
    
        return d
