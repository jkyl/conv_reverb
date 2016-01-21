import audio

a = audio.Audio('samples/avril.aif')
b = audio.Audio('samples/cymbal.wav')
c = audio.Audio('impulses/hall.wav')
d = a.pitchshift(1.2).convolve(b).convolve(c).ringmod(7000)
d.write_to_wav('output/wtf.wav')
