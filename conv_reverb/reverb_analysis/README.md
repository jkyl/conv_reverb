# Reverb Analysis

Directory for reverb recognition analysis scripts and output files.

## Directories

* output/: Directory containing exported reverb signature of impulse responses and generated plots.

## Files

* example.py: Python script which automates impulse processing and showcases the reverb analysis.
* impulse_processing.py: Python script to process and export reverb signature of impulse responses.
* impulses.csv: Csv file containing a list of the impulses in ../impulses/.
* k_neighbors.py: Python script that implements a k-nearest neighbors analysis for frequency spectra.
* reverb_analysis.py: Python script that performs recognition of the reverb signature in a wet sound.
* test_reverb_analysis.py: Python script that tests the accuracy of the reverb analysis algorithm.

## tl;dr

Run <code>example.py</code> which will,

1. analyze the impulse responses in <code>../impulses/</code> using the <code>impulse_processing.py</code> script and export to disk their reverb signature,
2. run one example usage of the <code>reverb_analysis.py</code> script and return result while also generating an array of plots which are not shown but are saved to disk to <code>output/plots/</code>