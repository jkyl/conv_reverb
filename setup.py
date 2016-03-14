import subprocess
from sys import platform as PLATFORM


def unix_command(string):
    cmd = string.split(' ')
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()

print('Installing PyDub...')
if 'Python 2.7' in unix_command('python --version'):
    PIP_SUFFIX = ''
    out, err = unix_command('sudo -H pip install pydub')
else:
    PIP_SUFFIX = '2'
    out, err = unix_command('sudo -H pip2 install pydub')
if 'already satisfied' in out:
    print('PyDub already installed.')
    
print('Checking dependencies...')

if PLATFORM == 'darwin':
    out, err = unix_command('which brew')
    if 'no brew' in err:
        print('Installing homebrew...')
        unix_command('xcode-select -install')
        unix_command('sudo -H ruby -e "$(curl -fsSL \
        https://raw.githubusercontent.com/Homebrew/install/master/install)"')
        
    out, err = unix_command('brew list')
    if not 'libvorbis' and 'theora' and 'sdl' in out:
        print('Installing libav...')
        unix_command('sudo -H brew install libav --with-libvorbis --with-sdl --with-theora')
    
    out, err = unix_command('pip{} show matplotlib'.format(PIP_SUFFIX))
    if not 'Version: 1.5.1' in out:
        print('installing matplotlib 1.5.1...')
        unix_command('sudo -H pip{} install --upgrade matplotlib'.format(PIP_SUFFIX))

if 'linux' in PLATFORM:
    out, err = unix_command('dpkg -s libav-tools')
    if 'is not installed' in err:
        print('Installing libav...')
        unix_command('sudo -H apt-get -y install libav-tools')

    out, err = unix_command('pip{} show matplotlib'.format(PIP_SUFFIX))
    if not 'Version: 1.5.1' in out:
        print('Installing matplotlib 1.5.1...')
        unix_command('sudo -H apt-get -y install freetype*')
        out, err = unix_command('sudo -H pip{} install --upgrade matplotlib'.format(PIP_SUFFIX))
        print(out)
        print(err)
    
print('Complete.')
