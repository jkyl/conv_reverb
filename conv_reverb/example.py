import sys, os
from audio import Audio

if len(sys.argv) != 2:
    print('Usage: python3 example.py [file type .mp3, .wav, .aif, .ogg, etc.]')
fname = sys.argv[1]

print('\nExample script for the audio class.\n\n{}'.format('~'*40))
print('Loading in {}...'.format(fname))

a = Audio('samples/avril.aif')

print('\n{} is now inside an Audio object - you can read and write its time-series data.'.format(a.title))
print('\nBy default, it writes to both ./download_files/{}.wav and ../Web_Interface/static/temp.wav.'.format(a.title))
print('\nOn a mac, you can play audio from the command line with afplay. On ubuntu, you\'ll have to download vlc or another audio player.')
print('\nWriting now...')

a.write_to_wav()

print('\nNow let\'s load another Audio instance and convolve the two...')

b = Audio('impulses/Booth_atrium.wav')
c = a.convolve(b)
c.write_to_wav()

print('\nThe convolution has been written to ./download_files and its title has been formatted to reflect the transformation. If you use pitch shifting or ring modulation, these steps are the same except for the method you call and the args you give.\n')

c.plot_fft_spectrum()

print('\nThe running-windowed spectrogram of the convolution has also been written to ../Web_Interface/static/temp.png. If you enable MPL inline or interactive mode, you can see it without navigating there. Take a look if you please. Also, the "FutureWarning" is a MPL bug that has no effect on the plot.')

print('{}\n\nPlease check out test_correlation.py for a demonstration of one way we can determine the origin of a wet sound.\n\nBest,\nW.I.R.E. team.'.format('~'*40))
