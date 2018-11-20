#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import requests

try:
    from . import opengraph_library
except:
    import opengraph.opengraph as opengraph_library


#from opengraph.opengraph import OpenGraph as og
from ..web import Resource

def opengraph_extract(url_or_resource, og_tag):
    """
    Extracts via open graph scraping
    Use more than 2 packages to extract
    """
    
    resource = isinstance(url_or_resource, Resource) and url_or_resource or Resource(url_or_resource)
    
    def new_fetch(self, url):
        """Overriding the opengraph module fetch function"""
        cont = resource.get_contents()
        return self.parser(cont)
    
    opengraph_library.OpenGraph.fetch = new_fetch
    
    # Exception catching for missing schema and Keyerror
    try:
        open_graph_ins = opengraph_library.OpenGraph(url=resource.url)
        return open_graph_ins[og_tag]
    except (KeyError, requests.exceptions.MissingSchema):
        return None



if __name__ == "__main__" and len(sys.argv) >= 3:
    url = sys.argv[1]
    og_tag = sys.argv[2]
    print opengraph_extract(url, og_tag)
