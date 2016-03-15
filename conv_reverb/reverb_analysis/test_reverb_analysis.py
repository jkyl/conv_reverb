import sys, os
sys.path.append('../')
sys.path.append('../../')

import re, csv
import subprocess

import audio, reverb_analysis

SOUND_DIR = '../samples/'
IMPULSES_CSV = 'impulses.csv'
WET_SOUNDS_CSV = '../wet_sounds/wet_sounds.csv'
K = 3

print(''' 
SCRIPT TO TEST THE REVERB RECOGNITION ANALYSIS

Usage: python test_reverb_analysis.py 
Alternative usage: python test_reverb_analysis.py <k>

where <k> is a positive integer for k-neighbors.

If the correct reverb signature is present within the top three 
results returned, this script will count it as successful hit.

Note: If you change the test audio file within the script make sure to save it to ../impulses/

''')

print('~~~~~~~~')

####### PART 1 OF THE TESTING SCRIPT ################

print('''

This initial test will apply a convolution reverb to a dry sound
and test the reverb recognition analysis on this "wet" sound.

''')

input('Press enter to continue')

reader = csv.reader(open(IMPULSES_CSV))
impulse_fnames = [row[0] for row in reader]

fname = 'avril.aif'
audio_file = audio.Audio(SOUND_DIR + fname)

# Update k neighbors
if len(sys.argv) == 2:
    K = int(sys.argv[1])
    
impulses_audio = []
for impulse in impulse_fnames:
    impulse = audio.Audio('../impulses/' + impulse)
    impulses_audio.append(impulse)

hits = total = 0.
for impulse in impulses_audio:
    conv = audio_file.convolve(impulse)
    conv._set_title('{} convolved with {}'.format(fname[:-4], impulse.title))

    print('~~~~~~~~')
    print('Testing \"{}\"...'.format(conv.title))
    print('')

    conv.write_to_wav(custom='output/wavfiles/{}.wav'.format(conv.title))
    results = reverb_analysis.go('output/wavfiles/{}.wav'.format(conv.title), k=K)

    os.remove('output/wavfiles/{}.wav'.format(conv.title))

    hits_this_round = total_this_round = 0.

    for key in results:
        if key != impulse.title:
            if impulse.title in results.keys():
                hits_this_round += 1.

                # This is for a more punishing hits_this_round
                # procedure which only awards hits for a top match
#                if results[impulse.title] < results[key]:
#                    hits_this_round += 1.

            total_this_round += 1.
    print('{}% ({} out of {})'.format(int(round(hits_this_round * 100./total_this_round)), int(hits_this_round), int(total_this_round)))
    hits += hits_this_round
    total += total_this_round
print('______________________________________________________')
print('\ntotal accuracy: {}% ({} out of {})\n'.format(int(round(hits * 100./total)), int(hits), int(total)))

print('~~~~~~~~')

####### PART 2 OF THE TESTING SCRIPT ################

print('''

This second part will test the reverb recognition analysis on real wet sounds with natural reverb.

NOTE: The real wet sounds are really bad quality with a lot of noise.

''')

input('Press enter to continue')

reader = csv.reader(open(WET_SOUNDS_CSV))
wet_sounds = [row[0] for row in reader]

wet_sound_impulses = {'avril_ida_noyes_patio.wav': 'Ida_noyes_patio',
'avril_rockefeller_center_mono.wav': 'Rockefeller_center',
'avril_rockefeller_center_stereo.wav': 'Rockefeller_center',
'avril_rockefeller_side.wav': 'Rockefeller_side',
'avril_saieh_hall.wav': 'Saieh_hallway',
'woop_rockefeller_side.wav': 'Rockefeller_side'}

hits = total = 0.
for wet_sound in wet_sounds:

    print('~~~~~~~~')
    print('Testing \"{}\"...'.format(wet_sound))
    print('')

    results = reverb_analysis.go('../wet_sounds/{}'.format(wet_sound), k=K)

    hits_this_round = total_this_round = 0.

    for key in results:
        if key != wet_sound_impulses[wet_sound]:
            if wet_sound_impulses[wet_sound] in results.keys():
                hits_this_round += 1.

            total_this_round += 1.
    print('{}% ({} out of {})'.format(int(round(hits_this_round * 100./total_this_round)), int(hits_this_round), int(total_this_round)))
    hits += hits_this_round
    total += total_this_round
print('______________________________________________________')
print('\ntotal accuracy: {}% ({} out of {})\n'.format(int(round(hits * 100./total)), int(hits), int(total)))


