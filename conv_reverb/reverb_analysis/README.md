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

## Accuracy of the reverb recognition analysis

```sh
$ python test_reverb_analysis.py
```