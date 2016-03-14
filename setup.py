import subprocess
from sys import platform as PLATFORM


def unix_command(string):
    cmd = string.split(' ')
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()

print('Installing pip...')
unix_command('sudo python get-pip.py')

print('Installing PyDub...')
if unix_command('pip show pydub')[0].decode('utf-8') != '':
    print('PyDub already installed.')
else:
    unix_command('sudo pip install pydub')
    
print('Checking dependencies...')
if PLATFORM == 'darwin':
    out, err = unix_command('which brew')
    if 'no brew' in err.decode('utf-8'):
        print('Installing homebrew...')
        unix_command('sudo xcode-select -install')
        unix_command('sudo ruby -e "$(curl -fsSL \
        https://raw.githubusercontent.com/Homebrew/install/master/install)"')
        
    out, err = unix_command('brew list')
    if not 'libvorbis' and 'theora' and 'sdl' in out.decode('utf-8'):
        print('Installing libav...')
        unix_command('sudo brew install libav --with-libvorbis --with-sdl --with-theora')
    
    out, err = unix_command('pip show matplotlib')
    if not 'Version: 1' in out.decode('utf-8'):
        print('Installing matplotlib 1.4.3...')
        unix_command('sudo pip uninstall -y python-dateutil')
        unix_command('sudo pip uninstall -y matplotlib')
        unix_command('sudo pip install python-dateutil==2.2')
        unix_command('sudo pip install matplotlib==1.4.3')
    else:
        print('matplotlib version already > 1.')

if 'linux' in PLATFORM:
    out, err = unix_command('dpkg -s libav-tools')
    if 'is not installed' in err.decode('utf-8'):
        print('Installing libav...')
        unix_command('sudo apt-get -y install libav-tools')

    out, err = unix_command('pip show matplotlib')
    if not 'Version: 1' in out.decode('utf-8'):
        print('Installing matplotlib 1.4.3...')
        out, err = unix_command('sudo apt-get -y install freetype*')
        out, err = unix_command('sudo pip install matplotlib==1.4.3')
    else:
        print('matplotlib version already > 1.')

print('Complete.')
