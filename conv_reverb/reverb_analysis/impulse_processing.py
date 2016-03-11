#
# PYTHON 2.7
#
# This script is extracts the necessary information from the impulse responses
# (IRs) and exports them to disk for further analysis.
#

import sys
sys.path.append('../')

import csv
import numpy as np

# Project modules
import audio
from k_neighbors import FREQ_BINS, FFT_WINDOW_SIZE, plot


IMPULSES_DIR = '../impulses/'
IMPULSES_CSV = IMPULSES_DIR + 'impulses.csv'
PROCESSED_IMPULSES_DIR = 'output/processed_impulses/'
PROCESSED_IMPULSES_CSV = PROCESSED_IMPULSES_DIR + 'processed_impulses.csv'


class ImpulseResponses:
    '''
    Class to represent IRs, apply filtering and export.
    '''

    def __init__(self, impulses_csv):
        '''
        '''
        self.__impulse_fnames = self.read_csv(impulses_csv)
        self.__impulses_audio = self.get_audio(self.impulse_fnames)
        self.__impulses_ffts = self.get_ffts(self.impulses_audio)

        
    @property
    def impulse_fnames(self):
        '''
        '''
        return self.__impulse_fnames

    @property
    def impulses_audio(self):
        '''
        '''
        return self.__impulses_audio

    @property
    def impulses_ffts(self):
        '''
        '''
        return self.__impulses_ffts

        
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

            # remove initial part of title
            if impulse.title[:7] == 'impulse' and len(impulse.title)>7:
                impulse.title = impulse.title[8:]

        return impulses_audio

    
    def filter_low_decibels(self, impulse_fft):
        '''
        Filter out low decibel points (below -80 dB) from end of impulse.
        '''
        len_fft = len(impulse_fft)
        five_percent = len_fft / 20.

        for i in range(-1, -(len_fft+1), -1):
            if impulse_fft[i] > -80 and abs(i) >= five_percent:
                impulse_fft = impulse_fft[:i]
                break

        return impulse_fft


    def get_ffts(self, impulses_audio):
        '''
        '''
        impulses_fft = {}

        for impulse in impulses_audio:
            impulses_fft[impulse.title] = {}
            impulse_fft = impulse.get_fft(window_size_in_samples=FFT_WINDOW_SIZE)

            for freq_bin in FREQ_BINS:
                filtered_fft = self.filter_low_decibels(impulse_fft[freq_bin])
#                plot(filtered_fft, '{}_bin_{}'.format(impulse.title, freq_bin)) #
                impulses_fft[impulse.title][str(freq_bin)] = filtered_fft

        return impulses_fft

    
    def export_filenames(self, filenames):
        '''
        '''
        with open(PROCESSED_IMPULSES_CSV, 'w') as csvfile:
            writer = csv.writer(csvfile)

            for filename in filenames:
                writer.writerow([filename + '.npz'])

    
    def export_to_npz(self):
        '''
        '''
        filenames = []
        
        for impulse in self.impulses_ffts:
                processed_impulse = []

                for freq_bin in FREQ_BINS:
                    freq_fft = self.impulses_ffts[impulse][str(freq_bin)]
                    processed_impulse.append(freq_fft)

                # export processed_impulse for future analysis
                np.savez(PROCESSED_IMPULSES_DIR + '{}.npz'.format(impulse), processed_impulse)
                filenames.append(impulse)

        # export filenames to csv for future import
        self.export_filenames(filenames)
    
    
def go(impulses_csv):
    '''
    '''
    if impulses_csv == '':
        impulses = ImpulseResponses(IMPULSES_CSV)
        impulses.export_to_npz()
    else:
        impulses = ImpulseResponses(impulses_csv)
        impulses.export_to_npz()


if __name__=='__main__':

    if len(sys.argv) not in (1, 2):
        print "usage: python2 {} <impulses.csv>".format(sys.argv[0])
        print "alternative usage: python2 {}".format(sys.argv[0])
        sys.exit(1)

    if len(sys.argv) == 2:
        go(sys.argv[1])
    else:
        go('')
