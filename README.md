# &mdash;WIRE&mdash; Web Interfaced Reverb Engine

A Web interfaced reverb engine. Part of an ongoing project for CMSC 12200 at the Univerity of Chicago.

## How to run

<em>Instructions are based on an OS X system running Python 2.7 with pip and homebrew installed.</em>

Required python modules are numpy, SciPy and, matplotlib (5.1). Make sure you have them updated to their latest versions.

Additional modules and libraries required can be installed as instructed below.

```sh
$ pip install pydub
$ brew install ffmpeg --with-libvorbis --with-ffplay --with-theora
```

## Current state of the project

1/24/16: Early stages of development. Still designing what we want the project to be.

3/5/16: Reverb engine complete. Correlation analysis complete. Reverb analysis in progress. Web front-end in progress.

## To-do list

* Add lots of documentation.
* Create bash script that installs dependencies.
* Create a master script that communicates front-end to backend.
* Make API script save files to samples/
* Make sure everything runs in a CS 122 Virtual Machine.
* Prep for the final presentation.
* Reference some website that explains the signal processing concepts that this project uses.
* Record real wet sounds across campus spaces for analysis.

## Known issues


