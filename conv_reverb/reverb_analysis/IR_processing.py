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

def read_csv(impulses_fname):
    '''
    '''
    reader = csv.reader(open(impulses_fname))
    impulses = [row[0] for row in reader]
    return impulses

def get_audio(impulses):
    '''
    '''
    impulses_audio = []
    
    for impulse in impulses:
        impulse = audio.Audio(IMPULSES_DIR + impulse)
        impulses_audio.append(impulse)

    return impulses_audio

def get_fft(impulses_audio):
    '''
    '''
    impulses_fft = {}

    for impulse in impulses_audio:
        fft = impulse.get_fft()
        impulses_fft[impulse.title] = fft

    return impulses_fft

def filter_decibels(impulse_fft):
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

def plot(fft, title):
    '''
    '''
    X = np.linspace(0, 2*len(fft)/44100., len(fft))

    plt.cla()
    ax = plt.axes()
    ax.set_yscale('linear')
    ax.set_title(title)
    ax.scatter(X, fft, c='brown')
    plt.savefig('output/plots/{}.png'.format(title))
    
    
def go(impulses_fname):
    '''
    '''
    impulses = read_csv(impulses_fname)
    impulses_audio = get_audio(impulses)
    impulses_fft = get_fft(impulses_audio)

    freq_bins = [5,10,15,20,25]

    for impulse_fft in impulses_fft:
        processed_impulse = []
        
        for freq_bin in freq_bins:
            freq_fft = impulses_fft[impulse_fft][freq_bin]
            filtered_fft = filter_decibels(freq_fft)
            plot(filtered_fft, '{}_bin_{}'.format(impulse_fft, freq_bin)) #
            processed_impulse.append(filtered_fft)

        # export processed impulse for future analysis
        np.savez('output/processed_IRs/{}.npz'.format(impulse_fft), processed_impulse)


if __name__=='__main__':

    if len(sys.argv) != 2:
        print "usage: python2 {} <impulses filename>".format(sys.argv[0])
        sys.exit(1)
    
    go(sys.argv[1])
