#
# This script has the classes necessary to perform reverb analysis in the frequency
# domain.
#
# All code in this script represents original code unless otherwise specified.
#

import sys
sys.path.append('../')

import csv
import numpy as np
from types import *

# Project modules
import audio
import k_neighbors
from k_neighbors import FREQ_BINS, FFT_WINDOW_SIZE, MIN_LENGTH, K_NEIGHBORS, plot
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
        Inilializes instance of ProcessedImpulses where impulses_fname
        is a .csv with the names of processed impulses.
        '''
        self.__fnames = self.build_fnames(impulses_fname)
        self.__impulses = self.import_impulses()

    @property
    def impulses(self):
        '''
        Getter.
        '''
        return self.__impulses

    @property
    def fnames(self):
        '''
        Getter.
        '''
        return self.__fnames

    
    def build_fnames(self, impulses_fname):
        '''
        Read the filenames of impulses from csv.
        '''
        reader = csv.reader(open(impulses_fname))
        fnames = [row[0] for row in reader]
        return fnames

    
    def import_impulses(self):
        '''
        Import impulses saved as .npz to numpy arrays.
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
    Class to represent an audio file with a reverb signature.
    In this class lie the methods necessary to extract the reverb signature
    of an audio file.
    '''
    def __init__(self, audio_fname):
        '''
        Inilializes instance of ReverbAudio where audio_fname
        is a .csv with the names of an audio file with reverb.
        '''
        self.__def_val = None
        self.__audio = audio.Audio(audio_fname)
        self.__fft = self.audio.get_fft(window_size_in_samples=FFT_WINDOW_SIZE)
        self.__processed_fft = self.process_fft()
        self.__reverb_signature = self.extract_reverb_signature()

    @property
    def audio(self):
        '''
        Getter.
        '''
        return self.__audio
    
    @property
    def fft(self):
        '''
        Getter.
        '''
        return self.__fft

    @property
    def processed_fft(self):
        '''
        Getter.
        '''
        return self.__processed_fft

    @property
    def reverb_signature(self):
        '''
        Getter.
        '''
        return self.__reverb_signature

    @property
    def def_val(self):
        '''
        Getter.
        '''
        return self.__def_val


    def filter_low_decibels(self, freq_fft, cluster_size=5, step_size=1):
        '''
        Filter out low decibel points (below -80 dB) from end of audio.
        This method is more intelligent than the method by the same name 
        in the ImpulseResponses class.
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
        For the frequency bins in FREQ_BINS, clean the FFT sprectrum
        and assert it has the minimum length.
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
        For a given freq_fft check that the data is not too spread
        signifying an unclear or undefined reverb signal.
        This is carried out by checking the standard deviation at different
        time windows in the spectrum.
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
        Extracts a reverb signature for each FFT spectrum if there is a well defined one.
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
                    

def go(audio_fname, impulses_fname=PROCESSED_IMPULSES_CSV, k=K_NEIGHBORS, make_plots=False):
    '''
    Initializes a ProcessedImpulses object with the already processed impulses. 
    Initializes a ReverbAudio object using the audio_fname and extracts a reverb signature.
    Calls k_neihbors module to perform a k-nearest neighbors analysis between the impulses 
    and the audio reverb signature.
    Plots are generated if specified and saved to disk.
    '''
    impulses = ProcessedImpulses(impulses_fname)
    reverb = ReverbAudio(audio_fname)
    analysis = k_neighbors.KNeighbors(impulses.impulses, reverb.reverb_signature)
    analysis_results = analysis.do_analysis(k=k, make_plots=make_plots)

    # generate plots of the reverb signature at each frequency bin
    if make_plots:
        for freq_bin in FREQ_BINS:
            reverb_signature = reverb.reverb_signature[str(freq_bin)]
            if reverb_signature[0] != None:
                plot([reverb_signature], reverb.audio.title + '_bin_' + str(freq_bin))

    print('A lower value means a better match.')
    print('A value of 0.0 for k=1 means the match is exact.')
    print(analysis_results)
    return analysis_results


if __name__=='__main__':

    if len(sys.argv) not in (4, 5):
        print("usage: python3 {} <audio_file> <k_neighbors> <make_plots>".format(sys.argv[0]))
        print("alternative usage: python3 {} <audio_file> <impulses.csv> <k_neighbors> <make_plots>".format(sys.argv[0]))
        print("where <k_neighbors> is an integer number of neighbors for the analysis and,")
        print("where <make_plots> can be set to True or False.")
        print("IMPORTANT: your sound file must be saved to either conv_reverb/samples or conv_reverb/download_files.")
        sys.exit(1)


    if len(sys.argv) == 4:
        assert type(int(sys.argv[2])) is int,\
            '<k_neighbors> should be a positive integer and not {}'.format(sys.argv[2])

        assert sys.argv[3] in ('True', 'False'),\
            '<make_plots> should be set to either True or False and not {}.'.format(sys.argv[3])
            
        go(sys.argv[1], k=int(sys.argv[2]), make_plots=bool(sys.argv[3]))
        
    elif len(sys.argv) == 5:
        assert type(int(sys.argv[3])) is int,\
            '<k_neighbors> should be a positive integer and not {}'.format(sys.argv[3])

        assert sys.argv[4] in ('True', 'False'),\
            '<make_plots> should be set to either True or False and not {}.'.format(sys.argv[4])
        
        go(sys.argv[1], impulses_fname=sys.argv[2], k=int(sys.argv[3]), make_plots=bool(sys.argv[4]))
