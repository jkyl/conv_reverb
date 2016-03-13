#
# PYTHON 2.7
#
# This script performs our own flavor of k nearest neighbors analysis.
#

import sys
sys.path.append('../')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Project modules
import audio

MIN_LENGTH = 86 # minimum post_processed freq_fft time length for effective reverb analysis, 1 sec
CLUSTER_SIZE = 10 # number of samples used to compute statistics
FFT_WINDOW_SIZE = 512
FREQ_BINS = [5,10,15,20,25] # frequency bins for which the reverb
                            # signature of each impulse is most clear and on
                            # which analysis is conducted
MEAN_THRESHOLD = 0.97 # proportion about which reverb_mean can fluctuate from reverb_impulse
                      # or vice versa

# NOTES
#
# make it work with 'k' neighbors
# make sure you are implementing the 'k' neighbors analysis right
# normalize position based on center of mass from cluster of initial points
# do analysis should return a dictionary of the top three most likely spaces


class KNeighbors:
    '''
    '''
    def __init__(self, impulses, reverb):
        '''
        '''
        self.__def_val = None
        self.__impulses = impulses
        self.__reverb = reverb
        self.__analysis = self.do_analysis()

    @property
    def def_val(self):
        '''
        '''
        return self.__def_val
        
    @property
    def impulses(self):
        '''
        '''
        return self.__impulses

    @property
    def reverb(self):
        '''
        '''
        return self.__reverb

    @property
    def analysis(self):
        '''
        '''
        return self.__analysis
    
    
    def process_ffts(self, reverb, impulse, cluster_size=CLUSTER_SIZE):
        '''
        Processing involves matching both ffts to begin at roughly the same
        decibel level and truncate to be the same length.
        '''
        # does this actually matter?
        assert cluster_size <= MIN_LENGTH,
            'cluster_size={} is larger than MIN_LENGTH={}'.format(cluster_size,\
                                                                  MIN_LENGTH)
        if reverb[0] == self.def_val or impulse[0] == self.def_val:
            return self.def_val, self.def_val
        elif len(reverb) < MIN_LENGTH or len(impulse) < MIN_LENGTH:
            return self.def_val, self.def_val
        else:
            len_reverb = len(reverb)
            len_impulse = len(impulse)
            
            while len(reverb) >= MIN_LENGTH and len(impulse) >= MIN_LENGTH:
                reverb_cluster = reverb[:cluster_size]
                impulse_cluster = impulse[:cluster_size]

                reverb_mean = np.mean(reverb_cluster)
                impulse_mean = np.mean(impulse_cluster)

                if (MEAN_THRESHOLD * reverb_mean) > impulse_mean:
                    reverb = reverb[cluster_size:]
                elif (MEAN_THRESHOLD * impulse_mean) > reverb_mean:
                    impulse = impulse[cluster_size:]
                    

                    


            
    def distance(self, point_1, point_2):
        '''
        Euclidean distance where point_1 and point_2 are tuples (x,y).
        '''
        diff_1 = point_1[0] - point_2[0]
        diff_2 = point_1[1] - point_2[1]
        dist = np.sqrt((diff_1)**2 + (diff_2)**2)
        return dist


    def k_neighbors(self, reverb, impulse, k=3):
        '''
        '''
        if reverb[0] == self.def_val or impulse[0] == self.def_val:
            return self.def_val
        else:

            distances = []

            for i in range(len(reverb)):
                sub_distances = []
                if i == 0:
                    sub_distances.append(self.distance((reverb[i],i),
                                                       (impulse[i],i)))
                    sub_distances.append(self.distance((reverb[i],i),
                                                       (impulse[i+1],i+1)))
                elif i == len(reverb) - 1:
                    break
                else:
                    sub_distances.append(self.distance((reverb[i],i),
                                                       (impulse[i],i)))
                    sub_distances.append(self.distance((reverb[i],i),
                                                       (impulse[i+1],i+1)))
                    sub_distances.append(self.distance((reverb[i],i),
                                                       (impulse[i-1],i-1)))
                distances.append(np.mean(sub_distances))

            return np.mean(distances)


    def format_results(self, analysis, num_results=3):
        '''
        '''
        assert num_results < len(analysis), \
            'Number of results should be {} or less'.format(len(analysis))
        
        min_results = [np.float('inf')] * num_results
        best_impulses = [''] * num_results

        for impulse in analysis:
            for i in range(num_results):
                if analysis[impulse] < min_results[i]:
                    min_result[i] = analysis[impulse]
                    best_impulses[i] = impulse
                    break

        results = {}

        for i in range(num_results):
            results[best_impulse[i]] = min_results[i]

        return results
    

    def do_analysis(self, cluster_size=CLUSTER_SIZE, k=3, num_results=3):
        '''
        Performs k nearest neighbors analysis and returns the three most
        likely impulses to generate the reverb signature.
        k defaults to 3.
        '''
        analysis = {}
        
        for impulse in self.impulses:
            results = []
            
            for freq_bin in FREQ_BINS:
                reverb, impulse = self.process_ffts(self.reverb[str(freq_bin)],
                                                    self.impulses[impulse][str(freq_bin)],
                                                    cluster_size=cluster_size)
                result = self.k_neighbors(reverb, impulse, k=k)
                plot([reverb, impulse], impulse + '_bin_' + str(freq_bin)) # for visual testing
                
                if result != self.def_val:
                    results.append(result)

            analysis[impulse] = np.mean(results)

        return self.format_results(analysis, num_results=num_results)


# Function get_nice_colors and documentation extracted from CMSC 12100 2015
# PA7 debate_tweets.py
def get_nice_colors(n_colors):
    '''
    This function generates colors that can be passed to matplotlib functions
    that accept a list of colors. The function takes one parameter: the number
    of colors to generate. Using this function should result in the same colors
    shown in the assignment writeup.
    '''
    return cm.Accent([1 - (i/float(n_colors)) for i in range(n_colors)])

    
def plot(ffts, title):
    '''
    '''
    num_freq_bins = (FFT_WINDOW_SIZE / 2) + 1
    
    plt.cla()
    ax = plt.axes()
    ax.set_yscale('linear')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Intensity (dB)')
    ax.set_title(title)

    max_time = 0
    colors = get_nice_colors(len(ffts))

    for fft, color in zip(ffts, colors):
        len_fft = len(fft)
        X = np.linspace(0, 2 * num_freq_bins * len_fft/44100., len_fft)
        if np.max(X) > max_time:
            max_time = np.max(X)
        ax.scatter(X, fft, c=color)
    
    ax.set_xlim([-0.25, max_time+0.25])
    plt.savefig('output/plots/{}.png'.format(title))

    
if __name__=='__main__':

    print "This script contains the class and methods to perform k nearest neighbors analysis."
    print "The script is called within reverb_analysis.py"

        
