# Reverb Analysis

Directory for reverb recognition analysis scripts and output files.

## Directories

* <code>output/</code>: Directory containing exported reverb signature of impulse responses and generated plots.

## Files

* <code>example.py</code>: Python script which automates impulse processing and showcases the reverb analysis.
* <code>impulse_processing.py</code>: Python script to process and export reverb signature of impulse responses.
* <code>impulses.csv</code>: Csv file containing a list of the impulses in <code>../impulses/</code>.
* <code>k_neighbors.py</code>: Python script that implements a k-nearest neighbors analysis for frequency spectra.
* <code>reverb_analysis.py</code>: Python script that performs recognition of the reverb signature in a wet sound.
* <code>test_reverb_analysis.py</code>: Python script that tests the accuracy of the reverb analysis algorithm.

## tl;dr

Run <code>example.py</code> which will,

1. analyze the impulse responses in <code>../impulses/</code> using the <code>impulse_processing.py</code> script and export to disk their reverb signature,
2. run one usage example of the <code>reverb_analysis.py</code> script and return the results of the recogniztion algorithm while also generating a set of plots saved to disk to <code>output/plots/</code>.

```sh
$ python example.py
```

Subsequently run <code>test_reverb_analysis.py</code> which will produce an accuracy rating for the algorithm at recognizing the correct reverb signature of a wet sound.

```sh
$ python test_reverb_analysis.py
```

## Accuracy of the reverb recognition analysis

In order to test the accuracy of the reverb recognition analysis you can execute <code>test_reverb_analysis.py</code> as instructed above which has a verbose output and details its process.

In essence, it will check how accurate it is at successfully recognizing the reverb signature for sounds whose reverb was produced by the convolution reverb and for sounds that have a natural reverb signature (i.e. they were played and recorded within a space with reverb). <em>If the correct reverb signature is present within the top three results, it will count that as successful hit.</em>

The algorithm is more effective at recognizing the reverb if this was produced by the convolution reverb.

At the moment it outputs an accuracy rating of ..., meaning that ...% of the time it recognizes the correct reverb signature within its top three choices.

## How it works

Because this procedure is unique to this project we walk you through an overall view of the reverb analysis algorithm.

### Processing the impulse responses

The impulse responses contain the most clear information about the reverb of a space. This reverb can be visualized as the decay of the intensity in a given frequency bin. We found that the reverb decay is most clear in the lower range of frequency bins corresponding to frequencies in the hundreds of Hz.

Below is an image of the spectrum of Booth_atrium in the 10th frequency bin. The x-axis is time in seconds and the y-axis is intensity in decibels.
![Unprocessed impulse](output/readme_plots/Booth_atrium_bin_10.png "Frequency bin 10 of Booth_atrium")

This needs to be processed to get rid of the meaningless points below -80 dB. <code>impulse_processing.py</code> does this automatically for every impulse at the desired frequency bins.
![Processed impulse](output/readme_plots/Booth_atriumbin_10.png "Frequency bin 10 of Booth_atrium")

The impulse responses are now processed and the resulting reverb signature is exported to disk for future usage.

Having done that we can visualize the similarities and differences between these reverb signatures.

![Reverb signatures](output/readme_plots/processed_impulses_bin_10.png "Reverb signatures at frequency bin 10")

Each color in the above plot represents a different reverb space. The challenge is clear from this image: the reverb signatures are distinct but have similar structure (i.e. they cluster across the time domain with the same behavior generally speaking).

That is the challenge of the reverb recognition analysis, a challenge which is met using a k-nearest neighbors appraoch.

### The wet sound

You can provide a wet sound. A wet sound needs to have a reverb associated with it. This reverb can originate naturally from a space or it can be simulated by means of the convolution reverb.

The next step is to extract the reverb signature from the wet sound. This is best done in the final seconds from the sound ending since it is here that the source signal fully stops and the reflection signals remain.

Below is the full length frequency spectrum at bin 10 of the avril.aif sound file convolved with Booth_atrium.wav.

![Avril full length](output/readme_plots/bin_10_avril_convolved_with_booth.png "Full length spectrum of avril.aif convolved with Booth atrium at frequency bin 10")




