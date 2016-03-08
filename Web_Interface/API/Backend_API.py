import sys
import os
#'/home/student/WIRE/conv_reverb/Web_Interface/internetarchive'
sys.path.insert(0,'/home/student/WIRE/conv_reverb/Web_Interface/')
import internetarchive as ia

MAX_SIZE = 20 * (10 ** 6) # max size of sound file in megabytes
SOUND_DIR = '../conv_reverb/aporee_files/'


def query_catalog(args_from_ui):
    '''
    Given the dictonary args_from_ui, query the catalog of radio-aporee-maps at
    the Internet Archive (archive.org).

    Inputs:
        args_from_ui: dict of keywords provided from the ui
    Returns:
        query_results: Search object containing results of the query
    '''
    #print(args_from_ui)
    
    query = 'collection:radio-aporee-maps '

    for arg in args_from_ui:

        keyword = args_from_ui[arg]
#        if len(keyword.split(' ')) > 1:
#            keyword = '"' + keyword  + '"'
        
        query = query + arg + ':' + keyword + ' '

    query_results = ia.search_items(query)
    return query_results


def download_item(identifier):
    '''
    Download the mp3 file associated with identifier from the catalog.
    
    Inputs:
        identifier: str, identifier for an Item object
    Returns:
    '''

    item = ia.get_item(identifier)
    f_name = ''

    # This loop finds the .mp3 associated with the audio file.
    for f in item.iter_files():
        if f.name[-4:] == '.mp3':
            f_name = f.name
            break
    
    f = item.get_file(f_name)

    if f.size <= MAX_SIZE:
        f.download(SOUND_DIR + f_name)
    else:
        print ('File size is', f.size, 'bytes')
        print ('File size exceeds', MAX_SIZE, 'bytes')


def format_output(query_results):
    '''
    Generate a tuple of lists from search_results.
    
    Inputs:
        query_results: Search object containing results from a query
    Returns:
        output: tuple
    '''
    print('this') 
    items = []
    item_fields = []
    attribute_fields = ['Title', 'Creator', 'Description']

    for result in query_results:
        identifier = result['identifier']
        item = ia.get_item(identifier)
        items.append(item)

    for item in items:
        title = item.metadata['title']
        creator = item.metadata['creator']
        description = item.metadata['description']

        item_fields.append([Title, Creator, Description])
    
    output = (attribute_fields, item_fields)

    print(output) #

    return output
    

if __name__ == "__main__":

    args_from_ui = {'title': 'berlin in snow'}
#    args_from_ui = {'title': 'berlin', 'date': '2015-04-06'}
    query_results = query_catalog(args_from_ui)
    format_output(query_results)
#    download_item('aporee_2039_2931')
    

    
