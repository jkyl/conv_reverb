import audio

impulses = "Booth_atrium.wav Cathey_learning_center.wav Classics_balcony_balloon.wav Classics_balcony_book.wav Cobb_circle_balloon.wav Cobb_circle_book.wav Harper_quad_balloon.wav Harper_quad_book.wav Ida_noyes_patio.wav Ida_noyes_stairs.wav Rockefeller_center.wav Rockefeller_far.wav Rockefeller_side.wav Ryerson_dome.wav Saieh_hallway.wav UChurch.wav"

impulses = impulses.split(' ')
impulses_audio = []

sound = audio.Audio('samples/avril.aif')


for impulse in impulses:
    impulse = audio.Audio('impulses/' + impulse)
    impulses_audio.append(impulse)

    
for impulse_1 in impulses_audio:

    impulse_1_conv = impulse_1.convolve(sound)
    
    for impulse_2 in impulses_audio:

        if impulse_1.title != impulse_2.title:
        
            if impulse_1_conv.correlate(impulse_1) > impulse_1_conv.correlate(impulse_2):
                print True
            else:
                print False


