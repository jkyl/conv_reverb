import audio
import numpy as np

# make this a csv file?
IMPULSES = "Booth_atrium.wav Cathey_learning_center.wav Classics_balcony_balloon.wav Classics_balcony_book.wav Cobb_circle_balloon.wav Cobb_circle_book.wav Harper_quad_balloon.wav Harper_quad_book.wav Ida_noyes_patio.wav Ida_noyes_stairs.wav Rockefeller_center.wav Rockefeller_far.wav Rockefeller_side.wav Ryerson_dome.wav Saieh_hallway.wav UChurch.wav"

IMPULSES = IMPULSES.split(' ')
impulses_audio = []

for impulse in IMPULSES:
    impulse = audio.Audio('impulses/' + impulse)
    impulses_audio.append(impulse)

for impulse in impulses_audio:

    fft = impulse.get_fft()
    fft_bin_10 = fft[10]
    len_fft = len(fft_bin_10)
    ten_percent = len_fft / 10

    # removing low decibel points (below -80 dB)
    for i in range(-1, -(len_fft+1), -1):
        if fft[i] >= -80 and abs(i) >= ten_percent:
            fft = fft[:i]
            break
    
    


    

if __name__=='__main__':

    
