import internetarchive as ia

MAX_SIZE = 10000000 # max size of sound file in bytes
SOUND_DIR = '../sound_engine/aporee_files/'


def query_catalog(args_from_ui):
    '''
    Given the dictonary args_from_ui, query the catalog of radio-aporee-maps at
    the Internet Archive (archive.org).

    Inputs:
        args_from_ui: dict of keywords provided from the ui
    Returns:
        query_results: Search object containing results of the query
    '''
    
    query = 'collection:radio-aporee-maps '

    for arg in args_from_ui:

#        keyword = args_from_ui[arg]
#        if len(keyword.split(' ')) > 1:
#            keyword = '"' + keyword  + '"'
        
        query = query + arg + ':' + args_from_ui[arg] + ' '

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

    for f in item.iter_files():
        if f.name[-4:] == '.mp3':
            f_name = f.name
            break
    
    f = item.get_file(f_name)

    if f.size <= MAX_SIZE:
        f.download(SOUND_DIR + f_name)
    else:
        print 'File size is', f.size, 'bytes'
        print 'File size exceeds', MAX_SIZE, 'bytes'


def format_output(query_results):
    '''
    Generate a tuple of lists from search_results.
    
    Inputs:
        query_results: Search object containing results from a query
    Returns:
        output: tuple
    '''

    attribute_fields = ['title', '']
    output = ([],[])

    pass
    

if __name__ == "__main__":

    args_from_ui = {'title': 'berlin', 'date': '2015-04-05'}
    query_results = query_catalog(args_from_ui)
    download_item('aporee_2039_2931')
    

    
