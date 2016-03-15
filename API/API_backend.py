#
# This script has the necessary functions to communicate with the 
# Internet Archive API to query their database and download files.
#
# All code in this script represents original code.
#
# Documentation on how to use the official python wrapper for the API
# (i.e. internetarchive 0.9.8) can be found in the link below
# https://pypi.python.org/pypi/internetarchive/0.9.8

import re
import internetarchive as ia

MAX_SIZE = 20 * (10 ** 6) # max size of sound file in megabytes
MAX_NUM_RESULTS = 20 # sets a max number of result to return from API search
SOUND_DIR = '../conv_reverb/download_files/'


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
        keyword = args_from_ui[arg]
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

    assert f_name != '', 'No .mp3 file associated with item {}.\
        Try a different item'.format(identifier)
    
    f = item.get_file(f_name)

    if f.size <= MAX_SIZE:
        f.download(SOUND_DIR + f_name)
        return f.name
    else:
        print('File size is', f.size, 'bytes')
        print('File size exceeds', MAX_SIZE, 'bytes')
        return None 


def format_output(query_results):
    '''
    Generate a tuple of lists from search_results.
    
    Inputs:
        query_results: Search object containing results from a query
    Returns:
        output: tuple
    '''

    items = []
    item_fields = []
    attribute_fields = ['ID', 'Title', 'Creator', 'Description']

    # restrict query results to MAX_NUM_RESULTS
    i = MAX_NUM_RESULTS
    for result in query_results:
        if i<= 0:
            break
        else:
            identifier = result['identifier']
            item = ia.get_item(identifier)
            items.append(item)
            i += -1

    for item in items:
        keys = item.metadata.keys()
        identifier = item.metadata['identifier']

        # not all items have a key for each of the following
        # so there is a need for checking
        if 'title' in keys:
            title = item.metadata['title']
        else:
            title = ''

        if 'creator' in keys:
            creator = item.metadata['creator']
        else:
            creator = ''

        if 'description' in keys:
            description = item.metadata['description']

            # remove html tag for line breaks
            description = re.split('<br />', description)
            description = " ".join(description)

        else:
            description = ''

        item_fields.append([identifier, title, creator, description])
    
    output = (attribute_fields, item_fields)
    
    return output
    

if __name__ == "__main__":

    # example usage on querying the API and downloading files

    # args_from_ui is in dictionary form where each key
    # represents a search field.
    # allowed search field can be found here
    # https://archive.org/advancedsearch.php
    args_from_ui = {'title': 'berlin in snow'}

    # query_catalog returns a search object which can
    # be iterated over to get each item matching the search
    query_results = query_catalog(args_from_ui)

    # format_output returns a tuple containing the results
    # this can be printed out to the terminal
    output = format_output(query_results)

    # download_item downloads the .mp3 file associated
    # with the identifier
    download_item('aporee_2039_2931')
