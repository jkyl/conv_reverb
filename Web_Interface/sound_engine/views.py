from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
import json
import traceback
from io import StringIO
import csv
import os
import sys
#'/home/student/WIRE/conv_reverb/Web_Interface/API/API/API_backend.py'
sys.path.insert(0,'/home/student/WIRE/conv_reverb/API/')
from API_backend import query_catalog, format_output, download_item
 
NOPREF_STR = '- - - - - - - - -'
SOUND_FILES_DIR = os.path.join(os.path.dirname(__file__), '..', 'sound_files')
COLUMN_NAMES = dict(
        title ='Title',
        id ='ID',
        creator ='Creator',
        description ='Description',
)

def _load_column(filename, col=0):
    """Loads single column from csv file"""
    with open(filename) as f:
        reader = csv.reader(f)
        col = [row[0] for row in reader]
        return col 

def _load_res_column(filename, col=0):
    """Load column from resource directory"""
    return _load_column(os.path.join(SOUND_FILES_DIR, filename), col=col)


def _build_dropdown(options):
    """Converts a list to (value, caption) tuples"""
    return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]

DATE = _build_dropdown([None, '01', '02', '03','04', '05', '06','07', '08', '09','10','11','12','13','14',
        '15','16','17','18', '19','20', '21','22','23','24','25','26','27','28','29','30','31'])
MONTH = _build_dropdown([None,'01', '02', '03','04', '05', '06','07', '08', '09','10','11','12'])
IMPULSE = _build_dropdown([None] + _load_res_column('impulses.csv'))
YEAR = _build_dropdown([None] + _load_res_column('year_list.csv'))



class PickDate(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.ChoiceField(label='Year', choices=YEAR, required=False),
                  forms.ChoiceField(label='Month', choices=MONTH, required=False), 
                  forms.ChoiceField(label='Date', choices=DATE, required=False))
        super(PickDate, self).__init__(fields=fields,*args,**kwargs)
    def compress(self, values):
        
        #if values[2] == '31' and (values[1] in ['February', 'April', 'June', 'September','November']):
            #raise forms.ValidationError('Selected month does not have 31 days')
        #if values[2] == '30' and values[1] == 'February':
            #raise forms.ValidationError('Selected month does not have 30 days')    
        return values        


class SearchForm(forms.Form):
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
            help_text='e.g. Sexy baritone with Latin American accent',
            required=False)
    '''
    From_date = PickDate(
            label='From',
            help_text='Select date in YYYY MM DD format',
            required=False,
            widget=forms.widgets.MultiWidget(
                widgets=(forms.widgets.Select(choices=YEAR),
                         forms.widgets.Select(choices=MONTH),
                         forms.widgets.Select(choices=DATE))))
    To_date = PickDate(
            label='To',
            help_text='Select date in YYYY MM DD format',
            required=False,
            widget=forms.widgets.MultiWidget(
                widgets=(forms.widgets.Select(choices=YEAR),
                         forms.widgets.Select(choices=MONTH),
                         forms.widgets.Select(choices=DATE))))
    '''

class PickResForm(forms.Form):
    ids = forms.CharField(label='Enter ID to download file', help_text='aporee_27258_31409', required=False)

class ProcessForm(forms.Form):
    impulses = forms.ChoiceField(label='Impulse Response', choices=IMPULSE, required=False)

def home(request):
    print('see')
    context = {}
    global res
    res = None
    if request.method == 'GET' and 'Search' in request.GET:
        print('koi')
        # create a form instance and populate it with data from the request:
        query_API = SearchForm(request.GET)
        #resform = PickResForm(request.GET)
        form2 = ProcessForm(request.GET)
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
            '''
            From_date = query_API.cleaned_data['From_date']
            if From_date:
                args['From_day'] = From_date[2]
                args['From_month'] = From_date[1]
                args['From_year'] = From_date[0]
            To_date = query_API.cleaned_data['To_date']
            if To_date:
                args['To_day'] = To_date[2]
                args['To_month'] = To_date[1]
                args['To_year'] = To_date[0]  
            '''       
            try:
                res = query_catalog(args)
                res = format_output(res)
                #res = res = (['ID', 'Title', 'Creator', 'Description'], [['aporee_27258_31409', 'Vallendar, Deutschland - church bells in distance', 'aporee@greg...', 'TASCAM DR-100mkII with integrated Mics'], ['aporee_16095_18673', 'Golzheim, Düsseldorf, Deutschland - Düsseldorf. Robert Schumann Hochschule, Krypta', 'Frank Schulte', 'Inside a basement chamber of the music school building which has been turned into a Krypta by the artist work of Emil Schult in five years work from 1995 to 2000. More information about the artist work and Krypta can be found here:http://www.emilschult.eu/<br />The sounds of the room heating and ventilation and music coming from the rehearsal chambers of the floor above. <br /><br />This recording is part of the exhibition project - sonic states <br />soundmap nrw - sonic states, topographic field recordings and art places'], ['aporee_8205_9978', 'Cnr Lorne St & Wellesley St', 'grant_n_is@hotma...', 'Atmospheric sounds emitted during construction of Auckland Art Gallery'], ['aporee_1391_17012', 'Berlin: Vermessungspunkt Maybachufer / Bürknerstraße - Klangvermessung Kreuzkölln ::: 12.07.2012 ::: 04:09', 'henrik schröder', ''], ['aporee_8627_10425', 'neoscenes: hip-hop dancers', 'John Hopkins', ''], ['aporee_5078_6501', 'friedelstraße: kids garden - the city, the country & me: percussion group at 10 years kids garden party', 'henrik schröder', 'the city, the country & me: september 30, 2009'], ['aporee_12635_14808', 'neoscenes: Nieuwmarkt', 'John Hopkins', ''], ['aporee_28866_33241', '泰順公園, Da’an Dist.,Taipei City - Market and Park', 'Wu,Tsan-Cheng', 'Traffic Sound, Sitting in the park, Near the traditional markets, Bird calls ,,<br />Binaural recordings ,Best with Headphone, Proposal to turn up the volume ,<br />Sony PCM D100+ Soundman OKM II ( SoundMap20150721-7) , recorded by Wu,Tsan-Cheng 吳燦政'], ['aporee_9458_11360', 'Czech Rep., Olomouc, Litovelska str., grade crossing', 'yankrticka@gma...', 'a grade crossing at night'], ['aporee_8579_10370', 'Island Hvar, helicopters above Stari Grad -  low flight', 'ranka mesaric', 'poeple in the street and cafes, crickets, helicopters'], ['aporee_14269_16609', 'Jefferson Park, Chicago, IL, USA - CTA Blue Line train from Jefferson Park to Addison', 'thaighaudio@gma...', 'Part of my morning commute on a Blue Line train beginning at Jefferson Park CTA station, through Addison station. Each station on this excerpt sits in the meridian of Interstate 90, known locally as the Kennedy Expressway.<br /><br />Tascam DR-40.'], ['aporee_8016_9783', 'Wroclaw, Cinema Hostel, backstreet parking lot', 'maciej janasik', 'taken form a window facing backyard of the building, parking lot and some construction'], ['aporee_19147_22233', 'Beitou, Taipei City - Traditional Ceremony', 'Wu,Tsan-Cheng', 'Temple Traditional Ceremony,Zoom H4n+ Soundman OKM II , ,Best with Headphone( SoundMap20130812-27) , recorded by Wu,Tsancheng'], ['aporee_18937_21969', '130724_01 - Arles In Black', 'Brice Maire', 'Arles In Black, 01<br />Audio tour of the exhibition of photographs by Sergio Larrain<br />Recording by Brice Maire'], ['aporee_8262_10035', 'Khartourm Pl', '365921437@...', 'water fall'], ['aporee_16756_19498', 'Norwich Cathedral Cloisters UK - The Cloisters', 'Richard Fair', "I thought it was peaceful outside sitting in the Cloisters. But I could hear the sounds of extractor fans from the cafe.<br />I don't know who or what made the sound just before yo hear the bells ring, but it spooked me!<br />Recorded on Olympus LS-11 with Roland CS-10EM binaural microphones.<br />Best heard with headphones."], ['aporee_19885_23137', 'Sintra, trail towards Castelo dos Mouros - rain in the forest', 'maciej janasik', 'heavy rain in the forest + birds. construction works sounds in the distance'], ['aporee_19271_22389', 'Yangmei Station - Station hall', 'Wu,Tsan-Cheng', 'in the Station hall , Sony PCM D50 + Soundman OKM II ,Best with Headphone( SoundMap20130814-28) , recorded by Wu,Tsancheng'], ['aporee_6196_7723', 'wind in the other dome', 'patrick mcginley', 'wind through a decaying geodesic dome, teufelsberg, berlin'], ['aporee_20849_24195', 'Jiaotong University Station,Shanghai - walking in the station', 'Wu,Tsan-Cheng', 'walking in the station, Binaural recording,Best with the Headphone ,Zoom H6+ Soundman OKM II ( SoundMap20131203-15) , recorded by 吳燦政 Wu,Tsancheng'], ['aporee_26061_30144', 'Jimowzod, Koto island - the waves', 'Wu,Tsan-Cheng', 'In the beach, Sound of the waves, <br />Best with Headphone, Proposal to turn up the volume ,<br />Zoom H2n MS +XY ( SoundMap20141029-38) , recorded by Wu,Tsan-Cheng 吳燦政'], ['aporee_26685_30788', '杉福漁港,Liuqiu Township - Waves and tides', 'Wu,Tsan-Cheng', 'Birds singing, Chicken sounds, Small fishing port,Small beach, Waves and tides<br />Best with Headphone, Proposal to turn up the volume ,<br />Zoom H2n MS+XY ( SoundMap20141102-43) , recorded by Wu,Tsan-Cheng 吳燦政'], ['aporee_3421_4697', 'Robert Schumanplein Brussels, Klanklandschap#2 (BAS)', 'basdecaluwe@hotma...', 'sent by basdecaluwe@hotma... at 28.03.2009 00:28'], ['aporee_28555_32903', 'Milwaukee20150628-2057 - Silent reflection for each of the victims of violence within the city - female, 44, shot', 'The Green Lama', 'Project - A Moment Of Silence Milwaukee 2015<br />http://aporee.org/maps/work/projects.php?project=amomentofsilencemke2015<br /><br />0628 Party at incident location, Wright & 35th SE.'], ['aporee_28340_32660', 'Zhongshan N. Rd., Tamsui Dist. - Traditional temple festivals', 'Wu,Tsan-Cheng', 'Traditional temple festivals, Firecrackers<br />Binaural recordings ,Best with Headphone, Proposal to turn up the volume ,<br />Sony PCM D100+ Soundman OKM II ( SoundMap20150621-2) , recorded by Wu,Tsan-Cheng 吳燦政'], ['aporee_25611_29667', 'Vauville, France - Galets Vauville', 'Nicolas Germain', 'People on the beach with little water streaming and smooth stones'], ['aporee_5570_7029', 'stromboli, ginostra - lots of birds in a tree', 'udo noll', 'early evening, lot of birds in a tree'], ['aporee_22819_26482', 'Watermael-Boitsfort, Belgique - Cité Floréal, un peu de chocolat?', 'Flavien Gillié', 'A woman at a window is giving chocolate to some workers on a construction site.<br />Tech Note : SD-702, AT-BP4025.'], ['aporee_16296_18896', '左岸八里碼頭, New Taipei City - Standing on the wave', 'Wu,Tsan-Cheng', 'Standing on the wave,Binaural recordings (SoundMap20120701-15), recorded by Wu,Tsancheng(http://www.soundandtaiwan.com)'], ['aporee_1390_10692', 'Berlin: Vermessungspunkt Friedelstraße / Maybachufer - Klangvermessung Kreuzkölln ::: 02.12.2010 ::: 19:26', 'henrik schröder', '']])
                resform = PickResForm()
                print(resform) 
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
        print('ok')
        resform = PickResForm(request.GET)
        print(resform)
        if resform.is_valid():
            file_id =resform.cleaned_data['ids']
            download = download_item(file_id)   

    

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
        #if resform.cleaned_data['ids']:
            #args2 = resform.cleaned_data['ids']
        #id_list = []
        #for item in result:
            #id_list.append(str(item[0]))
        #id_list = id_list.sort()
        #IDS = _build_dropdown([None] + id_list)

    context['query_API'] = query_API
    #context['form2'] = form2
    context['resform'] = resform
    print(query_API['Title'])
    print ('help?')
    return render(request, 'index.html', context)

   

    