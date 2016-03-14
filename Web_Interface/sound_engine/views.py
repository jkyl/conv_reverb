'''
Implement by calling python3 manage.py runserver from the Web_Interface directory
'''
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
import json
import traceback
from io import StringIO
import csv
import os
import sys
# construct absolute path of API directory 
API_path = os.path.abspath(__file__)[:-35] + 'API'
sys.path.insert(0, API_path)
from API_backend import query_catalog, format_output, download_item
Transform_path = os.path.abspath(__file__)[:-35] + 'conv_reverb'
sys.path.insert(0, Transform_path)
from array_transforms import convolve, correlate, pitchshift, ringmod
from audio import Audio  
Dload_path = Transform_path + '/download_files'
Impulse_path = Transform_path + '/impulses'

 
context = {}
NOPREF_STR = '- - - - - - - - -'
SOUND_FILES_DIR = os.path.join(os.path.dirname(__file__), '..', 'sound_files')
COLUMN_NAMES = dict(
        title ='Title',
        id ='ID',
        creator ='Creator',
        description ='Description',
)

def _build_dropdown(options):
    '''
    Converts a list to (value, caption) tuples
    '''
    return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]

class SearchForm(forms.Form):
    '''
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
    '''
    ids = forms.CharField(label='Enter ID to download file', help_text='e.g. aporee_27258_31409', required=False)

class Transform_Input(forms.Form):
    '''
    '''
    download_files = os.listdir(Dload_path)
    download_files.sort()
    download_list = _build_dropdown(download_files)
    impulse_files = os.listdir(Impulse_path)
    impulse_files.sort()
    impulse_files.remove('README.txt')
    process_list = ['Convolution', 'Pitch Shift', 'Ring Modulation']
    process_ops = _build_dropdown(process_list)
    impulse_list = _build_dropdown(impulse_files)
    process = forms.ChoiceField(label='Transformation', choices=process_ops, required=True)
    downloads = forms.MultipleChoiceField(label='Downloads', choices=download_list, required=False, widget= forms.CheckboxSelectMultiple)
    impulses = forms.MultipleChoiceField(label='U Chicago Impulse Responses', choices=impulse_list, required=False, widget= forms.CheckboxSelectMultiple)
    num = forms.FloatField(label='Enter Number', min_value=0.0, required=False)     
     
def home(request):
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
                if download != None:
                    message1 = "File " + download + " downloaded to conv_reverb/conv_reverb/aporee_files. Restart server to access this file for sound transformations."
                else:
                    message1 = "Sorry, download failed: file size is too large"  
            context['message1'] = message1
    
    trans_form = Transform_Input()
    
    if request.method == 'GET' and 'Transform' in request.GET:
        trans_form = Transform_Input(request.GET)
        impulse_files = os.listdir(Impulse_path)
        download_files = os.listdir(Dload_path)
        if trans_form.is_valid():
            sound_in = trans_form.cleaned_data['downloads'] + trans_form.cleaned_data['impulses']
            num_in = trans_form.cleaned_data['num']
            for i in range(len(sound_in)):
                if sound_in[i] in impulse_files:
                    sound_in[i] = Impulse_path + '/' + sound_in[i] 
                else:
                    sound_in[i] = Dload_path + '/' + sound_in[i]    
            if trans_form.cleaned_data['process'] == 'Convolution':
                sound1 = Audio(sound_in[0])
                print(sound1.title)
                sound2 = Audio(sound_in[1])
                #conv_sound = sound1.convolve(sound2)
                #print(conv_sound.title())


    


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

   

    