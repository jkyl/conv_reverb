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
from k_neighbors import FREQ_BINS, FFT_WINDOW_SIZE, MIN_LENGTH, plot
from impulse_processing import PROCESSED_IMPULSES_DIR, PROCESSED_IMPULSES_CSV

MIN_LENGTH = MIN_LENGTH * 2 # minimum pre_processed freq_fft time length for
                            # effective reverb analysis, 2 sec
GUESS_LENGTH = 310 # guess time length of 3.6 sec for reverb signature extraction
CLUSTER_SIZE = 50 # number of samples used to compute statistics
MEAN_THRESHOLD = 0.95 # proportion about which mean_1 can fluctuate from mean_2
STD_THRESHOLD = 0.15 # minimum permitted standard deviation


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
        self.__def_val = None
        self.__audio = audio.Audio(audio_fname)
        self.__fft = self.audio.get_fft(window_size_in_samples=FFT_WINDOW_SIZE)
        self.__processed_fft = self.process_fft()
        self.__reverb_signature = self.extract_reverb_signature()

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


    def filter_low_decibels(self, freq_fft, cluster_size=5, step_size=1):
        '''
        Filter out low decibel points (below -80 dB) from end of audio.
        '''
        len_fft = len(freq_fft)
        i = -cluster_size

        while len_fft >= cluster_size:

            if i == -cluster_size:
                cluster = freq_fft[i:]
            else:
                cluster = freq_fft[i:i+cluster_size]

            mean = np.mean(cluster)

            if mean > -80:
                if i == -cluster_size:
                    freq_fft = freq_fft[:]
                else:
                    freq_fft = freq_fft[:i+cluster_size]
                break
            
            i += -step_size
            len_fft += -step_size
            
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
                filtered_fft = np.array([self.def_val])

            processed_fft[str(freq_bin)] = filtered_fft

        return processed_fft

    
    def little_spread(self, freq_fft, cluster_size=3, step_size=1):
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
                cluster = freq_fft[i:i+cluster_size]

            # normalize std
            std = np.std(cluster) / (0.5 * _range)
            stds.append(std)

            i += -step_size
            len_fft += -step_size

        return np.mean(stds) < STD_THRESHOLD
        

    def extract_reverb_signature(self, cluster_size=CLUSTER_SIZE, step_size=CLUSTER_SIZE):
        '''
        Extracts a reverb signature.
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
                reverb = np.array([self.def_val])
                reverb_signature[str(freq_bin)] = reverb
                continue

            len_guess = len(reverb)
            i = 0
            
            while len_guess >= 2 * cluster_size:

                len_guess += -step_size
                
                cluster_1 = reverb[i:i+cluster_size]
                cluster_2 = reverb[i+cluster_size:i+(2*cluster_size)]

                mean_1 = np.mean(cluster_1) 
                mean_2 = np.mean(cluster_2)

                if (MEAN_THRESHOLD * mean_1) < mean_2:
                    if len_guess > MIN_LENGTH:
                        reverb = reverb[i+step_size:]
                        i = 0
                        continue
                    else:
                        break

                i += step_size

            if reverb[0] != self.def_val and self.little_spread(reverb):
                reverb_signature[str(freq_bin)] = reverb
            else:
                reverb_signature[str(freq_bin)] = np.array([self.def_val])

        return reverb_signature
                    

def go(audio_fname, impulses_fname=PROCESSED_IMPULSES_CSV):
    '''
    '''
    impulses = ProcessedImpulses(impulses_fname)
    reverb = ReverbAudio(audio_fname)
    analysis = k_neighbors.KNeighbors(impulses.impulses, reverb.reverb_signature)
#    return analysis.analysis
    print analysis.analysis

    # generate plots for visual testing
#    for freq_bin in FREQ_BINS:
#        reverb_signature = reverb.reverb_signature[str(freq_bin)]
#        if reverb_signature[0] != None:
#            plot([reverb_signature], reverb.audio.title + '_bin_' + str(freq_bin))


if __name__=='__main__':

    if len(sys.argv) not in (2, 3):
        print "usage: python2 {} <audio_file>".format(sys.argv[0])
        print "alternative usage: python2 {} <audio_file> <impulses.csv>".format(sys.argv[0])
        sys.exit(1)

    if len(sys.argv) == 3:
        go(sys.argv[1], impulses_fname=sys.argv[2])
    else:
        go(sys.argv[1])
