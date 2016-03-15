import os

print("This is an example script to showcase the reverb recognition analysis algorithm.")

file_name = 'avril_convolved_with_Booth_atrium.wav'
file_path = '../samples/{}'.format(file_name)

print('Running impulse_processing.py and generating plots.')
os.system('python3 impulse_processing.py True')

print('Runnin reverb_analysis.py with avril_convolved_with_Booth_atrium.wav and k=3 neighbors. \
Generating plots as well.')
os.system('python3 reverb_analysis.py {} 3 True'.format(file_path))


