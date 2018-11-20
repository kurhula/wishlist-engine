#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import sys
from amazon.api import AmazonAPI, AsinNotFound
from ..web import Resource

amazon_keys = AmazonAPI(
    'AKIAJ23XDVRFYQD5WRCQ',
    'kgmMQCoepQWrSffuK+mBO+Be+9kOl+cWgRPwPqdZ',
    'tiwariayushgi-20'
)
 
def amazon_api(url_or_resource, item):
    """Extracts metadata via amazon API scraping"""
    
    resource = isinstance(url_or_resource, Resource) and url_or_resource or Resource(url_or_resource)
    url = resource.url
    
    # Exception catching for invalid entry as url
    try:
        product_id_search = re.search(r'\bdp/([^/]+)\b', url)
    except TypeError:
        return None
    
    if product_id_search:
        product_id = product_id_search.group(1)
        
        # Exception catching in case the product_id_search is None or invalid
        try:
            product = amazon_keys.lookup(ItemId = product_id)
            if hasattr(product, item):
                return getattr(product, item)
            return None
        
        # Exception catching for invalid item name
        except AsinNotFound:
            return None
    else:
         return None

if __name__ == "__main__":
    url = sys.argv[1]
    item = sys.argv[2]
    print amazon_api_extract(url, item)
