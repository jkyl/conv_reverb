#
# This script is extracts the necessary information from the impulse responses
# (IRs) and exports them to disk for further analysis.
#
# All code in this script represents original code unless otherwise specified.
#

import sys
sys.path.append('../')

import csv
import numpy as np

# Project modules
import audio
from k_neighbors import FREQ_BINS, FFT_WINDOW_SIZE, plot


IMPULSES_DIR = '../impulses/'
IMPULSES_CSV = 'impulses.csv'
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
    
    
def go(impulses_csv=IMPULSES_CSV, make_plots=False):
    '''
    '''

    impulses = ImpulseResponses(impulses_csv)
    impulses.export_to_npz()

    # generate plots of the processed impulse response
    if make_plots:
        for freq_bin in FREQ_BINS:
            freq_impulses = []
            for impulse in impulses.impulses_ffts.keys():
                freq_impulse = impulses.impulses_ffts[impulse][str(freq_bin)]
                freq_impulses.append(freq_impulse)
                # plot each impulse at given frequency separately
                plot([freq_impulse], impulse + 'bin_{}'.format(freq_bin))
            # plot all impulses at given frequency together
            plot(freq_impulses, 'processed_impulses_bin_{}'.format(freq_bin))


if __name__=='__main__':

    if len(sys.argv) not in (2, 3):
        print("usage: python3 {} <make_plots>".format(sys.argv[0]))
        print("alternative usage: python3 {} <impulses.csv> <make_plots>".format(sys.argv[0]))
        print("where <make_plots> can be set to True or False.")
        sys.exit(1)

    if len(sys.argv) == 2:
        assert sys.argv[1] in ('True', 'False'),\
            '<make_plots> should be set to either True or False and not {}.'.format(sys.argv[1])

        go(make_plots=bool(sys.argv[1]))
            
    elif len(sys.argv) == 3:
        assert sys.argv[2] in ('True', 'False'),\
            '<make_plots> should be set to either True or False and not {}.'.format(sys.argv[2])

        go(make_plots=bool(sys.argv[2]))
