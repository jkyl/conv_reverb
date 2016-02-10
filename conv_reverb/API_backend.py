import internetarchive as ia

MAX_SIZE = 10000000 # max size of sound file in bytes


def query_catalog(keywords):
    '''
    Given the dictonary args_from_ui, query the catalog of radio-aporee-maps at
    the Internet Archive (archive.org).
    '''
    
    query = 'collection:"radio-aporee-maps" '

    for keyword in keywords:
        query = query + keyword + ':"' + keywords[keyword] + '" '

    query_results = ia.search_items(query)
    print query_results.query # 
    return query_results


def download_item(identifier):
    '''
    Download the mp3 file associated with identifier from the catalog.
    '''

    item = ia.get_item(identifier)
    f_name = ''

    for f in item.iter_files():
        if f.name[-4:] == '.mp3':
            f_name = f.name
            break
    
    f = item.get_file(f_name)

    if f.size <= MAX_SIZE:
        f.download('aporee_files/' + f_name)
    else:
        print 'File size is', f.size, 'bytes'
        print 'File size exceeds', MAX_SIZE, 'bytes'


def format_output(query_results):
    '''
    Generate a tuple of lists for the search results.
    '''

    attribute_fields = ['title', '']
    output = ([],[])

    pass
    

if __name__ == "__main__":

    args_from_ui = {}
    query_results = query_catalog(args_from_ui)
    download_item('aporee_2039_2931')
    

    
