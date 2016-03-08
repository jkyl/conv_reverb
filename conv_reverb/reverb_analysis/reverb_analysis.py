#
# This script...
#

import sys
sys.path.append('../')

import audio
import numpy as np
import matplotlib.pyplot as plt


IMPULSES_DIR = '../impulses/'
PROCESSED_IMPULSES = 'output/processed_IRs/processed_IRs.csv'
FREQ_BINS = [5,10,15,20,25] # these are low frequency bins for which the reverb
                            # signature of each IR is most clear


class ProcessedImpulse:
    '''
    '''
    def __init__(self):
        '''
        '''
        self.__impulses = self.import_processed_IRs()

    @property
    def impulses(self):
        '''
        '''
        return self.__impulses

    def import_processed_IRs(self):
        '''
        '''
        processed_impulse
        pass


def go(audio_fname):
    '''
    '''
    pass


if __name__=='__main__':

    if len(sys.argv) != 2:
        print "usage: python2 {} <audio_file>".format(sys.argv[0])
        sys.exit(1)
    
    go(sys.argv[1])
