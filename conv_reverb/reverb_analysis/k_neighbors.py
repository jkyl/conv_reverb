#
# PYTHON 2.7
#
# This script performs our own flavor of k nearest neighbors analysis.
#

import sys
sys.path.append('../')

import numpy as np
import matplotlib.pyplot as plt

# Project modules
import audio
                                    
FFT_WINDOW_SIZE = 512
FREQ_BINS = [5,10,15,20,25] # frequency bins for which the reverb
                            # signature of each IR is most clear and on
                            # which analysis is conducted                                    

# NOTES
#
# make plots have a good title, good axis labels, be scaled properly
# make it work with 'k' neighbors
# make sure you are implementing the 'k' neighbors analysis right
# normalize position based on center of mass from cluster of initial points
# do analysis should return a dictionary of the top three most likely spaces
                                    
class KNeighbors:
    '''
    '''
    def __init__(self, IRs, reverb_audio):
        '''
        '''
        self.__IRs = IRs
        self.__reverb_audio = reverb_audio
        self.__analysis = self.do_analysis()

    @property
    def IRs(self):
        '''
        '''
        return self.__IRs

    @property
    def reverb_audio(self):
        '''
        '''
        return self.__reverb_audio

    @property
    def analysis(self):
        '''
        '''
        return self.__analysis

    def truncate_fft(self, reverb_audio, impulse, title): #remove title
        '''
        '''
        if reverb_audio == None or impulse == None:
            return None, None
        else:
            if reverb_audio[0] > impulse[0]:
                i = 0
                while len(reverb_audio) > i:
                    if reverb_audio[i] <= impulse[i]:
                        reverb_audio = reverb_audio[i:]
                        break
                    else:
                        i += 1

            elif reverb_audio[0] < impulse[0]:
                i = 0
                while len(reverb_audio) > i:
                    if reverb_audio[i] >= impulse[i]:
                        impulse = impulse[i:]
                        break
                    else:
                        i += 1

            # you need to check it has the min required length

            if len(reverb_audio) < 170 or len(impulse) < 170:
                return None, None
            
            if len(reverb_audio) < len(impulse):
                plot(reverb_audio, impulse[:len(reverb_audio)], title) #
                return reverb_audio, impulse[:len(reverb_audio)]
            else:
                plot(reverb_audio[:len(impulse)], impulse, title) #
                return reverb_audio[:len(impulse)], impulse

    def distance(self, point_1, point_2):
        '''
        point_1 and point_2 are tuples (x,y)
        '''
        dist = np.sqrt((point_1[0]-point_2[0])**2+(point_1[1]-point_2[1])**2)
        return dist


    def k_neighbors(self, reverb_audio, impulse):
        '''
        '''
        if reverb_audio == None or impulse == None:
            return None
        else:
            # it is harcoded for k=3 at the moment, make it variable
            # this code is shit

            distances = []

            for i in range(len(reverb_audio)):
                sub_distances = []
                if i == 0:
                    sub_distances.append(self.distance((reverb_audio[i],i),
                                                       (impulse[i],i)))
                    sub_distances.append(self.distance((reverb_audio[i],i),
                                                       (impulse[i+1],i+1)))
                elif i == len(reverb_audio) - 1:
                    break
                else:
                    sub_distances.append(self.distance((reverb_audio[i],i),
                                                       (impulse[i],i)))
                    sub_distances.append(self.distance((reverb_audio[i],i),
                                                       (impulse[i+1],i+1)))
                    sub_distances.append(self.distance((reverb_audio[i],i),
                                                       (impulse[i-1],i-1)))
                distances.append(np.mean(sub_distances))

            return np.mean(distances)


    def do_analysis(self):
        '''
        '''
        analysis_results = {}
        
        for IR in self.IRs:
            results = []
            for freq_bin in FREQ_BINS:
                reverb_audio, impulse = self.truncate_fft(self.reverb_audio[str(freq_bin)],
                                                          self.IRs[IR][str(freq_bin)], IR + '_bin_' + str(freq_bin))
                result = self.k_neighbors(reverb_audio, impulse)
                if result != None:
                    results.append(result)

            analysis_results[IR] = sum(results)

        min_result = np.float('inf')
        best_IR = ''

        for IR in analysis_results:
            if analysis_results[IR] < min_result:
                min_result = analysis_results[IR]
                best_IR = IR

        return best_IR
                    

def plot_1(fft_1, fft_2, title):
    '''
    '''
    X = np.linspace(0, 2*257*len(fft_1)/44100., len(fft_1))

    plt.cla()
    ax = plt.axes()
    ax.set_yscale('linear')
    ax.set_title(title)
    ax.scatter(X, fft_1, c='brown')
    ax.scatter(X, fft_2, c='blue')
    plt.savefig('output/plots/{}.png'.format(title))

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

    

def plot_3(fft, title):
    '''
    '''
    X = np.linspace(0, 2*257*len(fft)/44100., len(fft))

    plt.cla()
    ax = plt.axes()
    ax.set_yscale('linear')
    ax.set_title(title)
    ax.scatter(X, fft, c='brown')
    plt.savefig('output/plots/{}.png'.format(title))  

        
