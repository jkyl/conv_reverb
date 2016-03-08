from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import json
import traceback
from io import StringIO
import csv
import os
#from operator import and_ ???
from functools import reduce
import sys
#'/home/student/WIRE/conv_reverb/Web_Interface/API/API/API_backend.py'
sys.path.insert(0,'/home/student/WIRE/conv_reverb/API/')
from API_backend import query_catalog, format_output
 
NOPREF_STR = '- - - - - - - - -'
SOUND_FILES_DIR = os.path.join(os.path.dirname(__file__), '..', 'sound_files')


'''
def _valid_result(res):
    """Validates results returned by find_courses"""
    (HEADER, RESULTS) = [0,1]
    ok = (isinstance(res, (tuple, list)) and 
          len(res) == 2 and
          isinstance(res[HEADER], (tuple, list)) and
          isinstance(res[RESULTS], (tuple, list)))
    if not ok:
        return False

    n = len(res[HEADER])
    def _valid_row(row):
        return isinstance(row, (tuple, list)) and len(row) == n
    return reduce(and_, (_valid_row(x) for x in res[RESULTS]), True)


def _valid_military_time(time):
    return (0 <= time < 2400) and (time % 100 < 60)
'''

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


'''

class IntegerRange(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.IntegerField())
        super(IntegerRange, self).__init__(fields=fields,
                                           *args, **kwargs)

    def compress(self, values):
        if values and (values[0] is None or values[1] is None):
            raise forms.ValidationError('Must specify both lower and upper '
                                        'bound, or leave both blank.')

        return values


class EnrollmentRange(IntegerRange):
    def compress(self, values):
        super(EnrollmentRange, self).compress(values)
        for v in values:
            if not (1 <= v <= 1000):
                raise forms.ValidationError('Enrollment bounds must be in the range 1 to 1000.')
        if values and (values[1] < values[0]):
            raise forms.ValidationError('Lower bound must not exceed upper bound.')
        return values


class TimeRange(IntegerRange):
    def compress(self, values):
        super(TimeRange, self).compress(values)
        for v in values:
            if not _valid_military_time(v):
                raise forms.ValidationError('The value {:04} is not a valid military time.'.format(v))
        if values and (values[1] < values[0]):
            raise forms.ValidationError('Lower bound must not exceed upper bound.')
        return values

RANGE_WIDGET = forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput,
                                                  forms.widgets.NumberInput))


class BuildingWalkingTime(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.ChoiceField(label='Building', choices=BUILDINGS, required=False),)
        super(BuildingWalkingTime, self).__init__(
                                           fields=fields,
                                           *args, **kwargs)

    def compress(self, values):
        if len(values) == 2:
            if values[0] is None or not values[1]:
                raise forms.ValidationError('Must specify both minutes and building together.')
            if values[0] < 0:
                raise forms.ValidationError('Walking time must be a non-negative integer.')
        return values
'''

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
    title = forms.CharField(
            label='Title',
            help_text='e.g. Argentinian National Anthem',
            required=False)
    uploader = forms.CharField(
            label='Uploader',
            help_text='e.g. Esteban',
            required=False)
    Description = forms.CharField(
            label='Description',
            help_text='e.g. Sexy baritone with Latin American accent',
            required=False)
    From_date = PickDate(
            label='From',
            help_text='e.g. For 31 January 2014 select 2014 01 31',
            required=False,
            widget=forms.widgets.MultiWidget(
                widgets=(forms.widgets.Select(choices=YEAR),
                         forms.widgets.Select(choices=MONTH),
                         forms.widgets.Select(choices=DATE))))
    To_date = PickDate(
            label='To',
            help_text='Select date as YYYY MM DD',
            required=False,
            widget=forms.widgets.MultiWidget(
                widgets=(forms.widgets.Select(choices=YEAR),
                         forms.widgets.Select(choices=MONTH),
                         forms.widgets.Select(choices=DATE))))


class ProcessForm(forms.Form):
    impulses = forms.ChoiceField(label='Impulse Response', choices=IMPULSE, required=False)

    '''
    enrollment = EnrollmentRange(
            label='Enrollment (lower/upper)',
            help_text='e.g. 1 and 40',#filter top results?
            widget=RANGE_WIDGET,
            required=False)
    time = TimeRange(
            label='Time (start/end)',
            help_text='e.g. 1000 and 1430 (meaning 10am-2:30pm)',
            widget=RANGE_WIDGET,
            required=False)
    time_and_building = BuildingWalkingTime(
            label='Walking time:', 
            help_text='e.g. 10 and RY (meaning at most a 10-minute walk from Ryerson).',
            required=False, 
            widget=forms.widgets.MultiWidget(
                widgets=(forms.widgets.NumberInput,
                         forms.widgets.Select(choices=BUILDINGS))))
    dept = forms.ChoiceField(label='Department', choices=DEPTS, required=False)
    days = forms.MultipleChoiceField(label='Days',
                                     choices=DAYS,
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)
    '''


def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        query_API = SearchForm(request.GET)
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
            #try:
            res = query_catalog(args)
            res = format_output(res)
            print(res)
            #except Exception as e:
            #    print('Exception caught')
            #    bt = traceback.format_exception(*sys.exc_info()[:3])
            #    context['err'] = """
            #    An exception was thrown in find_courses:
            #    <pre>{}
            #    {}</pre>
            #    """.format(e, '\n'.join(bt))
          
    else:
        query_API = SearchForm()
    if form2.is_valid():
        args2 = {}
    else:
        form2 = ProcessForm()        
    
    # Handle different responses of res
    if res is None:
        context['result'] = None
    '''

    elif isinstance(res, str):
        context['result'] = None
        context['err'] = res
        result = None
        cols = None
    
    elif not _valid_result(res):
        context['result'] = None
        context['err'] = ('Return of find_courses has the wrong data type. '
                         'Should be a tuple of length 4 with one string and three lists.')
    else:
        columns, result = res

        # Wrap in tuple if result is not already
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]
    ''' 
    context['query_API'] = query_API
    context['form2'] = form2
    return render(request, 'index.html', context)
    

