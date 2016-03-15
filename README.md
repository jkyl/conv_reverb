# &mdash;WIRE&mdash; Web Interfaced Reverb Engine

A Web interfaced convolution reverb engine. This project represents part of the requirements for CMSC 12200 at the Univerity of Chicago.

## List of dependencies needed

* Python 3.4 or above
* [internetarchive 0.9.8](http://bit.ly/1U2HJjU)
  * Run $ pip install -Iv internetarchive==0.9.8
* Django 1.9.1
* PyDub 0.16.3
* SciPy 0.17.0
* matplotlib 1.4.3
* libav tools
  * In Ubuntu run, $ sudo apt-get -y install libav-tools
  * In OS X run, $ brew install ffmpeg --with-libvorbis --with-ffplay --with-theora

## How to run in a CMSC 121 VM

<em>These instructions are based on a fresh CMSC 121 virtual machine.</em>

To automatically install the dependencies outlined above please run <code>setup.py</code> as instructed below.

```sh
$ python setup.py
```

It will ask you for sudo privileges which you should provide. This script may take a couple of minutes to run. It will print output of its current installation step.

## How to run in OS X

You can also run the project if you are running OS X. Just make sure to install the dependencies outlined above.

## Components of the project 

The project consists of four distinct components.

1. A Django based Web front. This part communicates with parts 2 and 3 of the project.
2. An API backend. This part communicates with the API provided by archive.org to access the contents of their database. We specifically access files associated with the [Radio Aporee project of world phonography](http://aporee.org/maps/). The API backend is able to query this database and download .mp3 items locally.
3. A convolution reverb engine. This part of the project contains the scripts necessary to represent audio files, perform sound transformations (i.e. convolution reverb, ring modulation and pitch shift) and generate spectrograms.
4. A reverb analysis engine which can analyze the reverb signature present in an audio file and perform a k-nearest neighbors based approach to find the closest matching impulse space to generate that reverb.

## How to run each of the different components

<em>Each directory in the project contains a <code>README</code> file with more descriptive steps on its contents and execution procedure. But here is an overall guideline.</em>


### Part 1 -- Web front

To run part 1, please proceed to the folder Web_Interface/ and run,

```sh
$ python manage.py runserver
```
and proceed to opening a browser window at the local host. This will initialize the Web interface server.


### Part 2 -- API backend

To run part 2 as a stand-alone script, please proceed to <code>API/</code> and open the script <code>API_backend.py</code> and inspect the bottom of the document which shows how to query the database and download files.

After making your desired modifications the script can be run with,

```sh
$ python API_backend.py
```
Make sure you add a <code>print</code> statement to the results generated.


### Part 3 -- Convolution reverb

The convolution reverb engine provides a lot of flexibility when operating it from a standalone perspective using <code>ipython</code> or a Python script.

```python
import audio

a = audio.Audio('samples/avril.aif')
b = audio.Audio('impulses/Booth_atrium.wav')
c = audio.Audio('impulses/Rockefeller_center.wav')

# apply sound transformations which can be chained one to another
d = a.pitchshift(1.2).convolve(b).convolve(c).ringmod(7000)

# plot a spectrogram
d.plot_waveform()

# write resulting sound transformation to file in disk
d.write_to_wav()
```

Please proceed to the <code>conv_reverb/</code> subfolder to find a more thorough <code>README</code> file.

## Known issues

* Upon upgrading our code from Python 2.7 to Python 3, the reverb analysis component of the project became erratic.

