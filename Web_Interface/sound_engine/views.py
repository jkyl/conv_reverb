#
# Usage: python3 manage.py runserver from the Web_Interface directory
#

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
import json
import traceback
from io import StringIO
import csv
import os
import sys
# construct absolute path of API directory in the given machine
API_path = os.path.abspath(__file__)[:-35] + 'API'
# enable modules in API directory to be imported
sys.path.insert(0, API_path)
from API_backend import query_catalog, format_output, download_item
# construct absolute path of conv_reverb directory in the given machine
Transform_path = os.path.abspath(__file__)[:-35] + 'conv_reverb'
# enable modules in conv_reverb directory to be imported
sys.path.insert(0, Transform_path)
from audio import Audio  
Dload_path = Transform_path + '/download_files'
Impulse_path = Transform_path + '/impulses'
Trans_aud_path = os.path.abspath(__file__)[:-35] + 'Web_Interface/output/transformed_wavs'

 
context = {}
NOPREF_STR = '- - - - - - - - -'
SOUND_FILES_DIR = os.path.join(os.path.dirname(__file__), '..', 'sound_files')
#column names used in table of results 
COLUMN_NAMES = dict(
        title ='Title',
        id ='ID',
        creator ='Creator',
        description ='Description',
)

#Directly from Gustav's ui/search/views.py in pa3
def _build_dropdown(options):
    '''
    Converts a list to (value, caption) tuples
    '''
    return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]

class SearchForm(forms.Form):
    '''
    Django form designed to accept search criteria from the user to query the API 
    '''
    Title = forms.CharField(
            label='Title',
            help_text='e.g. Argentinian National Anthem',
            required=False)
    Creator = forms.CharField(
            label='Creator',
            help_text='e.g. Esteban',
            required=False)
    Description = forms.CharField(
            label='Description',
            help_text='e.g. Baritone with Latin American accent',
            required=False)
    

class PickResForm(forms.Form):
    '''
    Django form class designed to accept user input of file id needed to download files through the API based on 
    search results.   
    '''
    ids = forms.CharField(label='Enter ID to download file', help_text='e.g. aporee_27258_31409', required=False)

class Transform_Input(forms.Form):
    '''
    Django form class customized to provide the user with options for different sound transformations and choices for 
    different sound files and values to implement the sound transformations
    '''
    download_files = [a for a in os.listdir(Dload_path) if '.mp3' in a]
    download_files.sort()
    download_list = _build_dropdown(download_files)
    impulse_files = os.listdir(Impulse_path)
    impulse_files.sort()
    impulse_files.remove('README.txt')
    process_list = ['Convolution', 'Pitch Shift', 'Ring Modulation', 'No Transformation']
    process_ops = _build_dropdown(process_list)
    impulse_list = _build_dropdown(impulse_files)
    trans_aud_list = os.listdir(Trans_aud_path)
    trans_aud_list.sort()
    trans_aud_list.remove('README.txt')
    trans_aud_ops = _build_dropdown(trans_aud_list)
    process = forms.ChoiceField(label='Transformation', choices=process_ops, required=True)
    downloads = forms.MultipleChoiceField(label='Downloads', choices=download_list, required=False, widget= forms.CheckboxSelectMultiple)
    impulses = forms.MultipleChoiceField(label='U Chicago Impulse Responses', choices=impulse_list, required=False, widget= forms.CheckboxSelectMultiple)
    trans = forms.MultipleChoiceField(label='Transformed Audio', choices=trans_aud_ops, required=False, widget= forms.CheckboxSelectMultiple)
    num = forms.FloatField(label='Enter Number', min_value=0.0, required=False)     

#heavily modified from Gustav's ui/search/views.py home function     
def home(request):
    '''
    Function to create objects of django forms and render them on the browser. Also, accesses user inputs and calls necessary functions 
    to process inputs and return results on the browser webpage. 
    '''
    res = None
    if request.method == 'GET' and 'Search' in request.GET:
        # create a form instance and populate it with data from the request:
        query_API = SearchForm(request.GET)
        resform = PickResForm()
        # check whether it's valid:
        if query_API.is_valid():
            # Convert form data to an args dictionary for API_backend
            args = {}
            if query_API.cleaned_data['Title']:
                args['Title'] = query_API.cleaned_data['Title']
            if query_API.cleaned_data['Creator']:
                args['Creator'] = query_API.cleaned_data['Creator']
            if query_API.cleaned_data['Description']:
                args['Description'] = query_API.cleaned_data['Description']
            
            try:
                res = query_catalog(args)
                res = format_output(res)
                resform = PickResForm()
            except Exception as e:
                print('Exception caught')
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in API_backend:
                <pre>{}
{}</pre>
                """.format(e, '\n'.join(bt))
                res = None     
             
    else:
        query_API = SearchForm()
        resform = PickResForm()
    if request.method == 'GET' and 'Download' in request.GET:
        resform = PickResForm(request.GET)
        if resform.is_valid():
            file_id =resform.cleaned_data['ids']
            if file_id == '':
                message1 = "Download not possible without ID. Please enter aporee ID to download file"
            else:    
                download = download_item(file_id)
                os.system('cp ../conv_reverb/download_files/{} ../conv_reverb/download_files/\!JUST_DOWNLOADED.mp3'.format(download)) #### here's where we cp -jk
                if download != None:
                    message1 = "File " + download + " downloaded to conv_reverb/conv_reverb/download_files."
                else:
                    message1 = "Sorry, download failed: file size is too large"  
            context['message1'] = message1
    
    trans_form = Transform_Input()
    
    if request.method == 'GET' and 'Transform' in request.GET:
        trans_form = Transform_Input(request.GET)
        impulse_files = os.listdir(Impulse_path)
        download_files = os.listdir(Dload_path)
        trans_aud_list = os.listdir(Trans_aud_path)
        if trans_form.is_valid():
            sound_in = trans_form.cleaned_data['downloads'] + trans_form.cleaned_data['impulses'] + trans_form.cleaned_data['trans']
            print(sound_in)
            num_in = trans_form.cleaned_data['num']
            for i in range(len(sound_in)):
                if sound_in[i] in impulse_files:
                    sound_in[i] = Impulse_path + '/' + sound_in[i] 
                elif sound_in[i] in download_files:
                    sound_in[i] = Dload_path + '/' + sound_in[i]
                else:
                    sound_in[i] = Trans_aud_path + '/' + sound_in[i]
            print(sound_in)
            # execute convolution of user specified audio files
            if trans_form.cleaned_data['process'] == 'Convolution':
                sound1 = Audio(sound_in[0])
                sound2 = Audio(sound_in[1])
                conv_sound = sound1.convolve(sound2)
                new_trans = Trans_aud_path + '/' + conv_sound.title + '.wav'
                conv_sound.write_to_wav()
                conv_sound.plot_fft_spectrum()
                message2 = "Transformed file saved as \"{}.wav\"".format(conv_sound.title)
            # execute pitch shift of user specified audio file and percent
            if trans_form.cleaned_data['process'] == 'Pitch Shift':
                sound = Audio(sound_in[0])
                ps_sound = sound.pitchshift(num_in)
                ps_sound.write_to_wav()
                ps_sound.plot_fft_spectrum()
                message2 = "Transformed file saved as \"{}.wav\"".format(ps_sound.title)
            # execute ring modulation of user specified audio file at desired frequency 
            if trans_form.cleaned_data['process'] == 'Ring Modulation':
                sound = Audio(sound_in[0])
                rm_sound = sound.ringmod(num_in)
                rm_sound.write_to_wav()
                rm_sound.plot_fft_spectrum()
                message2 = "Transformed file saved as \"{}.wav\"".format(rm_sound.title)
                
            if trans_form.cleaned_data['process'] == 'No Transformation':
                sound = Audio(sound_in[0])
                sound.write_to_wav()
                sound.plot_fft_spectrum()
                message2 = "Transformed file saved as \"{}.wav\"".format(sound.title)
                
            context['message2'] = message2

    


    # Handle different responses of res
    if res is None:
        context['result'] = None

    else:
        columns, result = res

        # Wrap in tuple if result is not already
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]
         
        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]
        
    context['query_API'] = query_API
    context['resform'] = resform
    context['transform'] = trans_form
    return render(request, 'index.html', context)

   

    
