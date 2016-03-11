#
# PYTHON 2.7
#
# This script has the classes necessary to perform reverb analysis in the frequency
# domain.
#

import sys
sys.path.append('../')

import csv
import numpy as np

# Project modules
import audio
import k_neighbors
from k_neighbors import FREQ_BINS, FFT_WINDOW_SIZE, plot
from impulse_processing import PROCESSED_IMPULSES_DIR, PROCESSED_IMPULSES_CSV

MIN_LENGTH = 171 # minimum freq_fft time length required for analysis, 2 sec
GUESS_LENGTH = 310 # guess time length of 3.6 sec for reverb signature extraction
CLUSTER_SIZE = 10 # number of samples used to compute statistics
                            
# NOTES
#
# make sure that you are getting a reverb signature with a good length
# make sure you are discarding reverb signature with too much fluctuation effectively
# make the standard deviation be a proportion of the range of values


class ProcessedImpulses:
    '''
    Class to represent processed impulse responses with a dictionary of each frequency
    bin studied.
    '''
    def __init__(self, impulses_fname):
        '''
        '''
        self.__fnames = self.build_fnames(impulses_fname)
        self.__impulses = self.import_impulses()

    @property
    def impulses(self):
        '''
        Getter for impulses.
        '''
        return self.__impulses

    @property
    def fnames(self):
        '''
        '''
        return self.__fnames

    
    def build_fnames(self, impulses_fname):
        '''
        '''
        reader = csv.reader(open(impulses_fname))
        fnames = [row[0] for row in reader]
        return fnames

    
    def import_impulses(self):
        '''
        '''
        impulses = {}
        for fname in self.fnames:
            fname = fname[:-4] # remove .npz extension from filename
            impulses[fname] = {}
            tmp = np.load(PROCESSED_IMPULSES_DIR + fname + '.npz')

            # freq_fft arrays are saved as a single array within the key 'arr_0'
            # in tmp
            for freq_fft, freq_bin in zip(tmp['arr_0'], FREQ_BINS):
                impulses[fname][str(freq_bin)] = freq_fft
                
        return impulses
        

class ReverbAudio:
    '''
    '''
    def __init__(self, audio_fname):
        '''
        '''
        self.__audio = audio.Audio(audio_fname)
        self.__fft = self.audio.get_fft(window_size_in_samples=FFT_WINDOW_SIZE)
        self.__processed_fft = self.process_fft()
        self.__reverb_signature = self.extract_reverb_signature()
        self.__def_val = np.array([None])

    @property
    def audio(self):
        '''
        '''
        return self.__audio
    
    @property
    def fft(self):
        '''
        '''
        return self.__fft

    @property
    def processed_fft(self):
        '''
        '''
        return self.__processed_fft

    @property
    def reverb_signature(self):
        '''
        '''
        return self.__reverb_signature

    @property
    def def_val(self):
        '''
        '''
        return self.__def_val


    def filter_low_decibels(self, freq_fft):
        '''
        Filter out low decibel points (below -80 dB) from end of audio.
        '''
        len_fft = len(freq_fft)
        i = - (CLUSTER_SIZE/2 + 1)

        while len_fft >= CLUSTER_SIZE:

            if i == -CLUSTER_SIZE:
                cluster = freq_fft[i:]
            else:
                cluster = freq_fft[i:i+10]

            mean = np.mean(cluster)

            if mean > -80:
                freq_fft = freq_fft[:i]
                break
            
        return freq_fft

    
    def process_fft(self):
        '''
        '''
        processed_fft = {}
        
        for freq_bin in FREQ_BINS:
            freq_fft = self.fft[freq_bin]
            
            if len(freq_fft) >= MIN_LENGTH:
                filtered_fft = self.filter_low_decibels(freq_fft)
            else:
                filtered_fft = self.def_val

            processed_fft[str(freq_bin)] = filtered_fft

        return processed_fft

    
    def assess_reverb_quality(self, freq_fft, cluster_size=3, step_size=1):
        '''
        '''        
        len_fft = len(freq_fft)
        _range = np.max(freq_fft) - np.min(freq_fft)
        stds = []

        # small cluster size
        i = -cluster_size
        while len_fft >= cluster_size:

            if i == -cluster_size:
                cluster = freq_fft[i:]
            else:
                cluster = freq_fft[i:i+3]

            # normalize std
            std = np.std(cluster) / (0.5 * _range)
            stds.append(std)

            i += -step_size
            len_fft += -step_size

        print np.mean(stds) #
        return np.mean(stds) < 0.05
        

    def extract_reverb_signature(self, cluster_size=CLUSTER_SIZE):
        '''
        '''
        reverb_signature = {}

        for freq_bin in FREQ_BINS:

            freq_fft = self.processed_fft[str(freq_bin)]
            len_fft = len(freq_fft)

            # make an initial guess for where the reverb is
            if len_fft >= GUESS_LENGTH:
                reverb = freq_fft[-GUESS_LENGTH:]
            elif len_fft >= MIN_LENGTH:
                reverb = freq_fft[:]
            else:
                reverb = self.def_val

            i = 0
            len_guess = len(reverb)
            final_i = len_guess - 2 * cluster_size
            
            while len_guess >= 2 * cluster_size:

                if i == final_i:
                    cluster_1 = freq_fft[i:i+cluster_size]
                    cluster_2 = freq_fft[i+cluster_size:i+(2*cluster_size)]
                    



----------
        reverb_signature = {}

        for freq_bin in FREQ_BINS:

            fft = self.processed_fft[str(freq_bin)]
            len_fft = len(fft)
            reverb = None
        
            i = -10
            while len_fft >= 20:
            
                cluster_1 = fft[i:i+10]
                cluster_2 = fft[i-10:i]
                mean_1 = abs(np.mean(cluster_1))
                mean_2 = abs(np.mean(cluster_2))
                std_1 = np.std(cluster_1)
                std_2 = np.std(cluster_2)

                
                if std_1 < 7 and std_2 < 7 and not (np.isnan(std_1)
                                                    or np.isnan(std_2)):

                    if mean_2 < (0.95 * mean_1) and len(fft[i:]) > 170: 
                        reverb = fft[i:]
                        break
                    else:
                        i += -10
                        len_fft += -10
                        
                else:
                    i += -1
                    len_fft += -1

            if reverb != None and not self.assess_reverb_quality(reverb):                                   
                reverb = None

            reverb_signature[str(freq_bin)] = reverb

        return reverb_signature
---------- 


def go(audio_fname, impulses_fname=PROCESSED_IMPULSES_CSV):
    '''
    '''
    processed_impulses = ProcessedImpulses(impulses_fname)
    reverb_audio = ReverbAudio(audio_fname)
#    analysis = k_neighbors.KNeighbors(processed_impulses.impulses, reverb_audio.reverb_signature)
    
    print analysis.do_analysis()
        
#    for freq_bin in FREQ_BINS:
#        reverb_signature = reverb_audio.reverb_signature[str(freq)]
#        if reverb_signature != None:
#            plot(reverb_signature, reverb_audio.audio.title + '_bin_' + str(freq))


if __name__=='__main__':

    if len(sys.argv) not in (2, 3):
        print "usage: python2 {} <audio_file>".format(sys.argv[0])
        print "alternative usage: python2 {} <audio_file> <impulses.csv>".format(sys.argv[0])
        sys.exit(1)

    if len(sys.argv) == 3:
        go(sys.argv[1], impulses_fname=sys.argv[2])
    else:
        go(sys.argv[1])
