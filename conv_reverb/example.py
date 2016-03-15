import sys, os
from audio import Audio

if len(sys.argv) != 2:
    print('Usage: python3 example.py [file type .mp3, .wav, .aif, .ogg, etc.]')
    sys.exit()
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

print('\nThe convolution has been written to ./download_files and its title has been formatted to reflect the transformation. You can also save to a custom directory with the optional "custom" argument in write_to_wav(). If you use pitch shifting, ring modulation, or delay, these steps are the same except for the method you call and the args you give.\n')

c.plot_fft_spectrum()

print('The running-windowed spectrogram of the convolution has been displayed onscreen and has also been written to ../Web_Interface/static/temp_wet.png. You can also view it on screen with either plt.ion() or %matplotlib inline. Take a look if you please.')

print('{}\n\nPlease check out test_correlation.py for a demonstration of one way we can determine the origin of a wet sound.\n\nBest,\nW.I.R.E. team.'.format('~'*40))
