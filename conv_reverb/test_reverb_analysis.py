import sys
sys.path.append('reverb_analysis/')

import audio, reverb_analysis, re, csv

IMPULSES_CSV = 'reverb_analysis/impulses.csv'
SOUND_DIR = 'samples/'
IMPULSES_FNAME = 'reverb_analysis/output/processed_impulses/processed_impulses.csv'
K = 3

print(''' 
SCRIPT TO TEST THE REVERB RECOGNITION ANALYSIS

Usage: python test_reverb_analysis.py 
Alternative usage: python test_reverb_analysis.py <k>

where <k> is a positive integer for k-neighbors.

Note: If you change the test audio file make sure to save it to ../impulses/

If the correct reverb signature is present within the top three 
results returned, this script will count it as successful hit.
''')

reader = csv.reader(open(IMPULSES_CSV))
impulse_fnames = [row[0] for row in reader]

fname = 'avril.aif'
if len(sys.argv) == 2:
    K = sys.argv[1]
    
audio_file = audio.Audio(SOUND_DIR + fname)

impulses_audio = []
for impulse in impulse_fnames:
    impulse = audio.Audio('impulses/' + impulse)
    impulses_audio.append(impulse)

hits = total = 0.
for impulse in impulses_audio:
    conv = audio_file.convolve(impulse)
    print('~~~~~~~~')
    conv._set_title(fname[:-4] + ' convolved with ' + impulse.title)
    print(conv.title)
    print('testing \"{}\"...'.format(conv.title))
    conv.write_to_wav()
    results = reverb_analysis.go('../Web_Interface/output/transformed_wavs/' + conv.title, \
                                    impulses_fname=IMPULSES_FNAME, k=K)

    hits_this_round = total_this_round = 0.

    for key in results:
        if key != impulse.title:
            if impulse.title in results.keys():
                if results[impulse.title] < results[key]:
                    hits_this_round += 1.
            total_this_round += 1.
    print('{}% ({} out of {})'.format(int(round(hits_this_round * 100./total_this_round)), int(hits_this_round), int(total_this_round)))
    hits += hits_this_round
    total += total_this_round
print('______________________________________________________')
print('\ntotal accuracy: {}% ({} out of {})\n'.format(int(round(hits * 100./total)), int(hits), int(total)))
