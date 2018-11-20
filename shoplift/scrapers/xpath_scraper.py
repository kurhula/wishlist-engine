#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import lxml, lxml.html
import requests
from ..web import Resource

def xpath_extract(url_or_resource, xpath_str):
    """Extracts via xpath scraping"""
    
    resource = isinstance(url_or_resource, Resource) and url_or_resource or Resource(url_or_resource)
    
    # Exceptions catching for missing schema
    try:
        page = resource.get_contents()
    except requests.exceptions.MissingSchema:
        return None
    tree = lxml.html.fromstring(page)
    
    # Handling error in case the given xpath is invalid
    try:
        product_val = tree.xpath(xpath_str)
        if isinstance(product_val, list) and len(product_val) <= 1:
            return len(product_val) and product_val[0] or None
        return product_val
    
    except (lxml.etree.XPathSyntaxError, lxml.etree.XPathEvalError):
        return None



if __name__ == "__main__" and len(sys.argv) >= 3:
    url = sys.argv[1]
    xpath_str = sys.argv[2]
    print xpath_extract(url, xpath_str)
