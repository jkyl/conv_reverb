import audio
import numpy as np



impulses = "Booth_atrium.wav Cathey_learning_center.wav Classics_balcony_balloon.wav Classics_balcony_book.wav Cobb_circle_balloon.wav Cobb_circle_book.wav Harper_quad_balloon.wav Harper_quad_book.wav Ida_noyes_patio.wav Ida_noyes_stairs.wav Rockefeller_center.wav Rockefeller_far.wav Rockefeller_side.wav Ryerson_dome.wav Saieh_hallway.wav UChurch.wav"

impulses = impulses.split(' ')
impulses_audio = []

for impulse in impulses:
    impulse = audio.Audio('impulses/' + impulse)
    impulses_audio.append(impulse)



def analyze_reverb(IR):

    
    


    


    

if __name__=='__main__':

    
