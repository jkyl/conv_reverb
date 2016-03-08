#
# This script...
#

import sys
sys.path.append('../')

import audio
import numpy as np
import matplotlib.pyplot as plt


IMPULSES_DIR = '../impulses/'
FREQ_BINS = [5,10,15,20,25] # these are low frequency bins for which the reverb
                            # signature of each IR is most clear


def import_processed_IRs():
    '''
    '''
    
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
