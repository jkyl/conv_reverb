import audio, sys
print(
'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SCRIPT TO TEST THE CORRELATION METHOD IN AUDIO.PY

Usage: python3 test_correlation.py [optional audio file name, defaults to avril.aif]

Percent values reported refer to the number of times a real impulse response (meaning the one
that was used to create the wet audio file) was correctly distunguished from an erroneous one,
divided by the total number of trials. Average for avril.aif is 85% currently. 

last edited JK 03/13
''')

impulses = "Booth_atrium.wav Cathey_learning_center.wav Classics_balcony_balloon.wav Classics_balcony_book.wav Cobb_circle_balloon.wav Cobb_circle_book.wav Harper_quad_balloon.wav Harper_quad_book.wav Ida_noyes_patio.wav Ida_noyes_stairs.wav Rockefeller_center.wav Rockefeller_far.wav Rockefeller_side.wav Ryerson_dome.wav Saieh_hallway.wav UChurch.wav"
impulses = impulses.split(' ')
impulses_audio = []

fname = 'samples/avril.aif'
if len(sys.argv) == 2:
    fname = sys.argv[1]
    
sound = audio.Audio(fname)
for impulse in impulses:
    impulse = audio.Audio('impulses/' + impulse)
    impulses_audio.append(impulse)

hits = total = 0.
for a in impulses_audio:
    conv = sound.convolve(a)
    print('~~~~~~~~')
    print('testing \"{}\"...'.format(conv.title))
    d = conv.correlate(impulses_audio)
    hits_this_round = total_this_round = 0.
    for key in d:
        if key != a.title:
            if d[a.title] > d[key]:
                hits_this_round += 1.
            total_this_round += 1.
    print('{}% ({} out of {})'.format(int(round(hits_this_round * 100./total_this_round)), int(hits_this_round), int(total_this_round)))
    hits += hits_this_round
    total += total_this_round
print('______________________________________________________')
print('\ntotal accuracy: {}% ({} out of {})\n'.format(int(round(hits * 100./total)), int(hits), int(total)))
        
