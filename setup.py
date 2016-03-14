import subprocess
from sys import platform as PLATFORM


def unix_command(string):
    cmd = string.split(' ')
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()


if 'Python 2.7' in unix_command('python --version')[0].decode('utf-8'):
    PIP_SUFFIX = ''
else:
    PIP_SUFFIX = '2'

    
print('Installing PyDub...')
if unix_command('pip show pydub')[0].decode('utf-8') != '':
    print('PyDub already installed.')
else:
    unix_command('sudo pip{} install pydub'.format(PIP_SUFFIX))

    
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
    
    out, err = unix_command('pip{} show matplotlib'.format(PIP_SUFFIX))
    if not 'Version: 1.4.3' in out.decode('utf-8'):
        print('Installing matplotlib 1.4.3...')
        unix_command('sudo pip{} uninstall -y python-dateutil'.format(PIP_SUFFIX))
        unix_command('sudo pip{} uninstall -y matplotlib'.format(PIP_SUFFIX))
        unix_command('sudo pip{} install python-dateutil==2.2'.format(PIP_SUFFIX))
        unix_command('sudo pip{} install matplotlib==1.4.3'.format(PIP_SUFFIX))

if 'linux' in PLATFORM:
    out, err = unix_command('dpkg -s libav-tools')
    if 'is not installed' in err.decode('utf-8'):
        print('Installing libav...')
        unix_command('sudo -H apt-get -y install libav-tools')

    out, err = unix_command('pip{} show matplotlib'.format(PIP_SUFFIX))
    if not 'Version: 1.' in out.decode('utf-8'):
        print('Installing matplotlib 1.4.3...')
        out, err = unix_command('sudo -H apt-get -y install freetype*')
        out, err = unix_command('sudo -H pip{} install matplotlib==1.4.3'.format(PIP_SUFFIX))
    
print('Complete.')
