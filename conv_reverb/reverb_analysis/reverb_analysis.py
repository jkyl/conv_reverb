#
# This script...
#

import sys
sys.path.append('../')

import csv
import audio
import numpy as np
import matplotlib.pyplot as plt


IMPULSES_DIR = '../impulses/'
PROCESSED_IMPULSES_DIR = 'output/processed_IRs/'
PROCESSED_IMPULSES = PROCESSED_IMPULSES_DIR + 'processed_IRs.csv'
FREQ_BINS = [5,10,15,20,25] # these are low frequency bins for which the reverb
                            # signature of each IR is most clear


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
        


def go(audio_fname):
    '''
    '''
    processed_impulses = ProcessedImpulses()
    print processed_impulses.impulses
    return processed_impulses


if __name__=='__main__':

    if len(sys.argv) != 2:
        print "usage: python2 {} <audio_file>".format(sys.argv[0])
        sys.exit(1)
    
    go(sys.argv[1])
