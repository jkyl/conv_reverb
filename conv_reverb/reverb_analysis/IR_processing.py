#
# This script is extracts the necessary information from the impulse responses
# (IRs) and exports them to disk for further analysis.
#

import sys
sys.path.append('../')

import csv
import numpy as np
import matplotlib.pyplot as plt

import audio
from reverb_analysis import FREQ_BINS


IMPULSES_DIR = '../impulses/'
IMPULSES_CSV = IMPULSES_DIR + 'impulses.csv'

# make it automatically generate a csv file of the exported filenames

class ImpulseResponses:
    '''
    Class to represent IRs, apply filtering and export.
    '''

    def __init__(self, impulses_csv):
        '''
        '''
        self.__impulse_fnames = self.read_csv(impulses_csv)

        
    def read_csv(self, impulses_csv):
        '''
        '''
        reader = csv.reader(open(impulses_csv))
        impulse_fnames = [row[0] for row in reader]
        return impulse_fnames

    
    def get_audio(self, impulse_fnames):
        '''
        '''
        impulses_audio = []

        for impulse in impulse_fnames:
            impulse = audio.Audio(IMPULSES_DIR + impulse)
            impulses_audio.append(impulse)

        return impulses_audio

    
    def filter_decibels(self, impulse_fft):
        '''
        '''
        len_fft = len(impulse_fft)
        ten_percent = len_fft / 10

        # filter out low decibel points (below -80 dB) from end of impulse
        for i in range(-1, -(len_fft+1), -1):
            if impulse_fft[i] >= -80 and abs(i) >= ten_percent:
                impulse_fft = impulse_fft[:i]
                break

        return impulse_fft


    def get_freq_fft(self, impulses_audio):
        '''
        '''
        impulses_fft = {}

        for impulse in impulses_audio:
            impulses_fft[impulse.title] = {}
            impulse_fft = impulse.get_fft()

            for freq_bin in FREQ_BINS:
                filtered_fft = self.filter_decibels(impulse_fft[freq_bin])
                impulses_fft[impulse.title][str(freq_bin)] = filtered_fft

        return impulses_fft

    

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
    
    
def go():
    '''
    '''

    impulses = ImpulseResponses(IMPULSES_CSV)
    
    impulses = read_csv(impulses_fname)
    impulses_audio = get_audio(impulses)
    impulses_fft = get_fft(impulses_audio)

    for impulse_fft in impulses_fft:
        processed_impulse = []
        
        for freq_bin in FREQ_BINS:
            freq_fft = impulses_fft[impulse_fft][freq_bin]
            filtered_fft = filter_decibels(freq_fft)
            plot(filtered_fft, '{}_bin_{}'.format(impulse_fft, freq_bin)) #
            processed_impulse.append(filtered_fft)

        # export processed impulse for future analysis
        np.savez('output/processed_IRs/{}.npz'.format(impulse_fft), processed_impulse)


if __name__=='__main__':

    if len(sys.argv) != 1:
        print "usage: python2 {}".format(sys.argv[0])
        sys.exit(1)
    
    go()
