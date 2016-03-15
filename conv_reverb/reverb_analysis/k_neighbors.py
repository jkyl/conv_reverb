#
# This script performs our own flavor of k nearest neighbors analysis.
#
# All code in this script represents original code unless otherwise specified.
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
MEAN_THRESHOLD = 0.98 # proportion about which reverb_mean can fluctuate from reverb_impulse
                      # or vice versa
K_NEIGHBORS = 3 # default number of k-neighbors to analyze


class KNeighbors:
    '''
    '''
    def __init__(self, impulses, reverb):
        '''
        '''
        self.__def_val = None
        self.__impulses = impulses
        self.__reverb = reverb

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
    
    
    def process_ffts(self, reverb, impulse, cluster_size=CLUSTER_SIZE, step_size=1):
        '''
        Processing involves matching both ffts to begin at roughly the same
        decibel level and truncate to be the same length.
        '''
        if reverb[0] == self.def_val or impulse[0] == self.def_val:
            return np.array([self.def_val]), np.array([self.def_val])
        elif len(reverb) < MIN_LENGTH or len(impulse) < MIN_LENGTH:
            return np.array([self.def_val]), np.array([self.def_val])
        else:
            while len(reverb) >= cluster_size and len(impulse) >= cluster_size:
                reverb_cluster = reverb[:cluster_size]
                impulse_cluster = impulse[:cluster_size]

                reverb_mean = np.mean(reverb_cluster)
                impulse_mean = np.mean(impulse_cluster)

                if reverb_mean > (MEAN_THRESHOLD * impulse_mean):
                    reverb = reverb[step_size:]
                elif impulse_mean > (MEAN_THRESHOLD * reverb_mean):
                    impulse = impulse[step_size:]
                else:
                    break

            # truncate to be same length
            if len(reverb) > len(impulse):
                reverb = reverb[:len(impulse)]
            else:
                impulse = impulse[:len(reverb)]
            
            if len(reverb) >= MIN_LENGTH:
                return reverb, impulse
            else:
                return np.array([self.def_val]), np.array([self.def_val])

            
    def distance(self, point_1, point_2):
        '''
        Euclidean distance where point_1 and point_2 are tuples (x,y).
        '''
        diff_1 = point_1[0] - point_2[0]
        diff_2 = point_1[1] - point_2[1]
        dist = np.sqrt((diff_1)**2 + (diff_2)**2)
        return dist


    def k_neighbors(self, reverb, impulse, k=K_NEIGHBORS):
        '''
        '''
        if reverb[0] == self.def_val or impulse[0] == self.def_val:
            return self.def_val
        else:
            len_reverb = len(reverb)
            distances = []

            if k % 2 == 0:
                is_even = True
            else:
                is_even = False
            
            for i in range(len_reverb):
                point_1 = (i, reverb[i])

                # first k/2 points
                if i <= (k//2 - 1):
                    sub_k = (2*i + 1)

                    if sub_k > k:
                        if is_even:
                            sub_k = k - 1
                        else:
                            sub_k = k

                    for j in range(-sub_k//2, sub_k//2 + 1, 1):
                        point_2 = (i+j, impulse[i+j])
                        dist = self.distance(point_1, point_2)
                        distances.append(dist)

                # last k/2 - 1 points
                elif i >= len_reverb - k//2:
                    sub_k = (2*(len_reverb-i-1) + 1)

                    if sub_k > k:
                        if is_even:
                            sub_k = k - 1
                        else:
                            sub_k = k

                    for j in range(-sub_k//2, sub_k//2 + 1, 1):
                        point_2 = (i+j, impulse[i+j])
                        dist = self.distance(point_1, point_2)
                        distances.append(dist)

                # points in between
                else:
                    if is_even:                        
                        for j in range(-k//2+1, k//2, 1):
                            point_2 = (i+j, impulse[i+j])
                            dist = self.distance(point_1, point_2)
                            distances.append(dist)

                        point_2_left = (i - k//2, impulse[i - k//2])
                        point_2_right = (i + k//2, impulse[i + k//2])

                        dist_left = self.distance(point_1, point_2_left)
                        dist_right = self.distance(point_1, point_2_left)

                        if dist_left < dist_right:
                            distances.append(dist_left)
                        else:
                            distances.append(dist_right)

                    else:
                        for j in range(-k//2, k//2 + 1, 1):
                            point_2 = (i+j, impulse[i+j])
                            dist = self.distance(point_1, point_2)
                            distances.append(dist)

            return np.mean(distances)                


    def format_results(self, analysis, num_results=3):
        '''
        '''
        assert num_results < len(analysis), \
            'Number of results should be {} or less'.format(len(analysis))
        
        min_results = [np.float('inf')] * num_results
        best_impulses = [''] * num_results

        
        
        for impulse in analysis:
            # get the index of the largest min value            
            max_min = np.max(min_results)
            max_min_i = np.where(min_results == max_min)[0][0]
            
            if analysis[impulse] < max_min:
                min_results[max_min_i] = analysis[impulse]
                best_impulses[max_min_i] = impulse

        results = {}

        for i in range(num_results):
            results[best_impulses[i]] = min_results[i]

        return results
    

    def do_analysis(self, cluster_size=CLUSTER_SIZE, k=K_NEIGHBORS, num_results=3, make_plots=False):
        '''
        Performs k nearest neighbors analysis and returns num_results number of most
        likely impulses to generate the reverb signature.
        k defaults to 3.
        '''
        analysis = {}
        
        for impulse in self.impulses:
            results = []
            impulse_name = impulse
            
            for freq_bin in FREQ_BINS:
                
                reverb, impulse = self.process_ffts(self.reverb[str(freq_bin)],\
                                                    self.impulses[impulse_name][str(freq_bin)],\
                                                    cluster_size=cluster_size)
                result = self.k_neighbors(reverb, impulse, k=k)
                
                # generate plots for the superposition of reverb_signature with impulse
                # at each frequency for visual testing
                if make_plots and reverb[0] != self.def_val and impulse[0] != self.def_val:
                    plot([reverb, impulse], impulse_name + '_bin_' + str(freq_bin))
                
                if result != self.def_val:
                    results.append(result)
                    
            if results != []:
                analysis[impulse_name] = np.mean(results)
            else:
                analysis[impulse_name] = np.float('inf')

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
    return cm.Accent([1 - (i/n_colors) for i in range(n_colors)])

    
def plot(ffts, title):
    '''
    '''
    num_freq_bins = (FFT_WINDOW_SIZE // 2) + 1
    
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

    print("This script contains the class and methods to perform k nearest neighbors analysis.")
    print("The script is called within reverb_analysis.py")

        
