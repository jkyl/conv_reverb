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
import matplotlib.pyplot as plt

import audio
#import k_neighbors


PROCESSED_IMPULSES_DIR = 'output/processed_impulses/'
PROCESSED_IMPULSES_CSV = PROCESSED_IMPULSES_DIR + 'processed_impulses.csv'

FFT_WINDOW_SIZE = 512
FREQ_BINS = [5,10,15,20,25] # frequency bins for which the reverb
                            # signature of each IR is most clear and on
                            # which analysis is conducted
                            
# NOTES
#
# solve the problem of the imports, which module imports which module
# make plots have a good title, good axis labels, be scaled properly
# make sure that you are getting a reverb signature with a good length
# make sure you are discarding reverb signature with too much fluctuation effectively
# make the standard deviation be a proportion of the range of values


class ProcessedImpulses:
    '''
    Class for dictionary of each impulse response with a dictionary of each frequency
    bin studied.
    '''
    def __init__(self):
        '''
        '''
        self.__filenames = self.build_filenames()
        self.__impulses = self.import_processed_IRs()

    @property
    def impulses(self):
        '''
        Getter for impulses.
        '''
        return self.__impulses

    @property
    def filenames(self):
        '''
        '''
        return self.__filenames

    def build_filenames(self):
        '''
        '''
        reader = csv.reader(open(PROCESSED_IMPULSES))
        filenames = [row[0] for row in reader]
        return filenames

    def import_processed_IRs(self):
        '''
        '''
        impulses = {}
        for filename in self.filenames:
            key = filename[:-4] # remove .npz extension from filename
            impulses[key] = {}
            tmp = np.load(PROCESSED_IMPULSES_DIR + filename)

            # freq_fft arrays are saved as single array within 'arr_0' key in tmp
            for freq_fft, bin_num in zip(tmp['arr_0'], FREQ_BINS):
                impulses[key][str(bin_num)] = freq_fft
                
        return impulses
        

class ReverbAudio:
    '''
    '''
    def __init__(self, audio_fname):
        '''
        '''
        self.__audio = audio.Audio(audio_fname)
        self.__fft = self.__audio.get_fft()
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

    def process_fft(self):
        '''
        '''
        processed_fft = {}
        
        for freq_bin in FREQ_BINS:
            freq_fft = self.fft[freq_bin]
            filtered_fft = self.filter_decibels(freq_fft)
            processed_fft[str(freq_bin)] = filtered_fft

        return processed_fft
        
    def filter_decibels(self, fft):
        '''
        '''
        len_fft = len(fft)
        five_percent = len_fft / 5

        # filter out low decibel points (below -80 dB) from end of audio
        for i in range(-1, -(len_fft+1), -1):
            if fft[i] >= -80: # and abs(i) >= five_percent:
                fft = fft[:i]
                break

        return fft

    def assess_reverb_quality(self, reverb_fft):
        '''
        '''
        len_fft = len(reverb_fft)
        stds = []

        i = -3
        while len_fft >= 3:

            cluster = reverb_fft[i:i+3]
            std = np.std(cluster)

            if not np.isnan(std):
                stds.append(std)
                
            i += -1
            len_fft += -1

        return np.mean(stds) < 3.1 # change it 
        

    def extract_reverb_signature(self):
        '''
        '''
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

#                print 'std1', std_1 #
#                print 'std2', std_2 #
                
                if std_1 < 7 and std_2 < 7 and not (np.isnan(std_1)
                                                    or np.isnan(std_2)):

                    if mean_2 < (0.95 * mean_1) and len(fft[i:]) > 170: # min time
                        reverb = fft[i:]
                        break
                    else:
                        i += -10
                        len_fft += -10
                        
                else:
                    i += -1
                    len_fft += -1

            if reverb != None and (not self.assess_reverb_quality(reverb)
                                   or len(reverb) > 300):
                reverb = None

            reverb_signature[str(freq_bin)] = reverb

        return reverb_signature


def plot_2(fft, title):
    '''
    '''
    num_freq_bins = (FFT_WINDOW_SIZE / 2) + 1
    len_fft = len(fft)
    X = np.linspace(0, 2 * num_freq_bins * len_fft/44100., len_fft)

    # normalize the scale for the plots

    plt.cla()
    ax = plt.axes()
    ax.set_yscale('linear')
    ax.set_title(title)
    ax.scatter(X, fft, c='brown')
    plt.savefig('output/plots/{}.png'.format(title))

    

def plot(fft, title):
    '''
    '''
    X = np.linspace(0, 2*257*len(fft)/44100., len(fft))

    plt.cla()
    ax = plt.axes()
    ax.set_yscale('linear')
    ax.set_title(title)
    ax.scatter(X, fft, c='brown')
    plt.savefig('output/plots/{}.png'.format(title))    


def go(audio_fname):
    '''
    '''
    processed_impulses = ProcessedImpulses()
    reverb_audio = ReverbAudio(audio_fname)
#    print reverb_audio.reverb_signature
    analysis = k_neighbors.KNeighbors(processed_impulses.impulses, reverb_audio.reverb_signature)
    
    print analysis.do_analysis()
    
    
#    for freq in FREQ_BINS:
#        reverb_signature = reverb_audio.reverb_signature[str(freq)]
#        print(reverb_signature)
#        if reverb_signature != None:
#            plot(reverb_signature, reverb_audio.audio.title + '_bin_' + str(freq))

if __name__=='__main__':

    if len(sys.argv) != 2:
        print "usage: python2 {} <audio_file>".format(sys.argv[0])
        sys.exit(1)
    
    go(sys.argv[1])
