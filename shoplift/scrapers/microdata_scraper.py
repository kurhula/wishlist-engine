#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys

try:
    from . import microdata_library
except ValueError:
    import microdata as microdata_library

import json
from ..web import Resource

def microdata_extract(url_or_resource, itemprop):
    """
    Extracts via microdata scraping
    Make sure to add two scrapers/packages in case one of them fails
    Use try-except for scarping
    """
    
    resource = isinstance(url_or_resource, Resource) and url_or_resource or Resource(url_or_resource)
    
    try:
        # Calling get_contents to get the html contents
        html_content = resource.get_contents_as_file()
        items = microdata_library.get_items(html_content)
    except ValueError:
        return None
    
    try:
        # Getting json data from the html content
        item = items[0]
        
        item_data = item.json()
        json_item_data = json.loads(item_data)
        try:
            itemprop = itemprop.split('/')
        except AttributeError:
            return None
        
        # Removing empty lists
        itemprop = [key for key in itemprop if key]
        
        itemprop_list = []
        for tag in itemprop:
            try:
                tag = int(tag)
                itemprop_list.append(tag)
            except ValueError:
                itemprop_list.append(tag)
                pass
        
        try:
            def f(iterable, key):
                return iterable[key]
            
            #Reducing the json data to required value   
            return reduce(f, itemprop_list, json_item_data)
        except IndexError:
            return None
        except KeyError:
            return None
    
    # Exception incase there is no microdata in the html content
    except IndexError:
        return None



if __name__ == "__main__" and len(sys.argv) >= 3:
    url = sys.argv[1]
    itemprop = sys.argv[2]
    print microdata_extract(url, itemprop)
