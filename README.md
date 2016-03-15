# &mdash;WIRE&mdash; Web Interfaced Reverb Engine

A Web interfaced convolution reverb engine. This project represents part of the requirements for CMSC 12200 at the Univerity of Chicago.

Jonathan Kyl, Esteban Zacharzewski, and Mayukh Sen

## How to run in a CMSC 121 VM

<em>These instructions are based on a fresh CMSC 121 virtual machine.</em>

To automatically install the dependencies outlined below please run <code>setup.py</code>.

```sh
$ python setup.py
```

It will ask you for sudo privileges which you should provide. This script may take a couple of minutes to run. It will print output of its current installation step.

## How to run in OS X

You can also run the project if you are running OS X. You can also run the <code>setup.py</code> script as outlined above. Otherwise make sure to install the necessary dependencies. You will need [homebrew](http://brew.sh/) in order to install libav tools; this script will attempt to install brew for you if it does not detect it.

## List of dependencies needed

* Python 3.4 or above
* [internetarchive 0.9.8](http://bit.ly/1U2HJjU)
  * Run <code>$ pip install -Iv internetarchive==0.9.8</code>
* Django 1.9.1
* PyDub 0.16.3
* SciPy 0.16.1
* matplotlib 1.4.3
* libav tools
  * In Ubuntu run <code>$ sudo apt-get -y install libav-tools</code>
  * In OS X run <code>$ brew install ffmpeg --with-libvorbis --with-ffplay --with-theora</code>



## Components of the project 

The project consists of four distinct components.

1. A Django based Web front. This part communicates with parts 2 and 3 of the project.
2. An API backend. This part communicates with the API provided by archive.org to access the contents of their database. We specifically access files associated with the [Radio Aporee project of world phonography](http://aporee.org/maps/). The API backend is able to query this database and download .mp3 items locally.
3. A convolution reverb engine. This part of the project contains the scripts necessary to represent audio files, perform sound transformations (i.e. convolution reverb, ring modulation and pitch shift) and generate spectrograms.
4. A reverb analysis engine which can analyze the reverb signature present in an audio file and perform a k-nearest neighbors based approach to find the closest matching impulse space to generate that reverb.

## How to run each of the different components

<em>Each directory in the project contains a <code>README</code> file with more descriptive steps on its contents and execution procedure. But here is an overall guideline.</em>


### Part 1 &mdash; Web front

To run part 1, please proceed to the folder <code>Web_Interface/</code> and run,

```sh
$ python manage.py runserver
```
and proceed to opening a browser window at the local host. This will initialize the Web interface server.


### Part 2 &mdash; API backend

To run part 2 as a stand-alone script (<em>although this is not intended</em>), please proceed to <code>API/</code> and open the script <code>API_backend.py</code> and inspect the bottom of the document which shows how to query the database and download files.

After making your desired modifications the script can be run with,

```sh
$ python API_backend.py
```
Make sure you add a <code>print</code> statement to the results generated.


### Part 3 &mdash; Convolution reverb

The convolution reverb engine provides a lot of flexibility when operating it from a standalone perspective using <code>ipython</code> or a Python script. Please proceed to the <code>conv_reverb/</code> subfolder and run <code>example.py</code> to showcase the engine.

Below is a brief example script on how to use the convolution reverb engine.

```python
import audio

a = audio.Audio('samples/avril.aif')
b = audio.Audio('impulses/Booth_atrium.wav')
c = audio.Audio('impulses/Rockefeller_center.wav')

# apply sound transformations which can be chained one to another
d = a.pitchshift(1.2).convolve(b).convolve(c).ringmod(7000).delay((.2, .5, .7))

# plot a spectrogram
d.plot_waveform()

# write resulting sound transformation to file in disk
d.write_to_wav()
```
The convolution (mulitplication in the frequency domain) is performed with an FFT algorithm, <em>O(NlogN)</em>. The spectrogram plotting method is meant to give a balance between resolution and speed. Towards this end we implemented a chain of overlapping [blackman windows](http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.blackman.html) atop the audio buffer. This way we get twice the time resolution per unit frequency resolution, as compared to non-overlapping windows.

### Part 4 &mdash; Reverb analysis

The reverb analysis component is not connected in any way to the Web front end at the moment. For this reason, the only possible way of running it is through the terminal or by importing the module in a script.

Please proceed to the directory <code>conv_reverb/reverb_analysis/</code> where you can run the following commands. You can also find an example script, <code>example.py</code>, which showcases the algorithm.

#### Impulse processing
Running the <code>impulse_processing.py</code> script studies the reverb signature of the impulse response sound files in <code>conv_reverb/impulses/</code> and saves this signature to disk (<code>conv_reverb/reverb_analysis/output/processed_impulses/</code>) for faster analysis thereafter.

```sh
$ python impulse_processing.py <make_plots>
```
where <code>\<make_plots></code> can be set to either <code>True</code> or <code>False</code>. The plots help visualize the processed impulses and are saved to <code>/conv_reverb/reverb_analysis/output/plots</code>.

#### Reverb analysis
Running the <code>reverb_analysis.py</code> script will perform a k-nearest neighbors approach to analyzing the reverb signature present in a <em>wet</em> audio file. It will return (and print) a dictionary with the three most likely spaces to produce the reverb and their associated match. A lower value means a better match. A value of 0.0 for k=1 means the match is exact. For this algorithm, consider it successful if it is able to return the correct impulse space among those three top results.

```sh
$ python reverb_analysis.py <audio_file> <k_neighbors> <make_plots>
```
where <code>\<audio_file></code> is the filename (and filepath) of an audio file you want to analyze, <code>\<k_neighbors></code> is a positive integer number of neighbors for the analysis and, <code>\<make_plots></code> can be set to <code>True</code> or <code>False</code>. The plots help visualize how the analysis is carried out and why a certain space was recognized over another. These plots are saved to <code>/conv_reverb/reverb_analysis/output/plots</code>.

#### Correlation analysis
We implemented another method for analysing a wet sound using cross-correlation. In <code>/conv_reverb/</code>, run

```sh
$ python test_correlation.py <audio_file (defaults to samples/avril.aif)>
```

to test the accuracy of this method. Internally the dry sound is convolved with each of our impulse responses in turn, and then correlated with the remaining impulse responses. The correlation waveform with the highest root-mean-square (RMS) is counted as the winner. In order to remove bias towards intrinsically more powerful impulse responses, the input waveforms are normalized to have the same RMS, then mean-subtracted and normalized to a standard deviation of 1. This method is 85% succesful on <code>avril.aif</code>, meaning that 85% of the time, the algorithm can distinguish between the impulse response with which the dry sound was convolved, and a red herring impulse response. All of this is done without performing a deconvolution or simply bookkeeping.

This method can also be called from an audio object. Suppose you've recorded a sound in a building off-campus, and you want to know which UChicago space the off-campus space most resembles, acoustically. In python you would run:
```python
import os
from audio import Audio

a = Audio('~/Desktop/My_Wet_Sound.wav')
dir = os.listdir('impulses/')
l = [Audio('impulses/' + f) for f in dir if '.wav' in f]
a.correlate(l)
```

which outputs a dictionary of all of our impulse responses along with the RMS's of their corresponding correlation waveforms. The one with the maximum RMS is the statistically most similar space. 
## Known issues

* ~~Upon upgrading our code from Python 2.7 to Python 3, the reverb analysis component and correlation method of the project became erratic. This was traced back to slightly different output generated by <code>scipy.signal.fftconvolve</code> between the Python 2 and 3 versions. We are currently working on this issue.~~

