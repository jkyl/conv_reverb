import os 
print (__file__)
print (os.path.dirname(os.path.abspath(__file__)))
print ((os.path.join(os.path.dirname(__file__))))
print ((os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sound_files')))
print (os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))