import internetarchive as ia


def search_items(kwds_dict):
    '''
    Given a dictonary of keywords, search the catalog of Internet Archive
    (archive.org). Returns a list of identifiers for items which matched criteria.
    '''
    
    search_terms = ''

    for kwd in kwds_dict:
        search_terms = search_terms + kwd + ':"' + kwds_dict[kwd] + '" '

    search = ia.search_items(search_terms)
    return search


def download_item(identifier):
    '''
    Given a string identifier, download item from catalog.
    '''

    item = ia.get_item(identifier)
    f = item.get_item()
    f.download('aporee_files/' + identifier + '.mp3')

    

if __name__ == "__main__":

    
