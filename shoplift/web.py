#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import re
import urlparse

import requests
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

session = CacheControl(
    requests.Session(),
    cache = FileCache('.webcache')
)



def sanitize_url(url):
    """Returns a sanitized and normalized version of the URL passed
    
    Adds missing scheme, lowercases the scheme and domain,
    and strips surrounding whitespace.
    """
    # TODO: strip fragment
    # TODO: canonical (sorted) query params
    
    # Remove whitespaces
    url = str(url).strip()
    
    parsed = urlparse.urlsplit(url)
    
    # Try and fix URLs with a missing scheme
    # eg:
    #   flipkart.com
    #   //example.com
    #   ://httpbin.org
    # but not:
    #   /amazon.com
    #   junglee
    #   .biz.info
    if not parsed.scheme and re.match(r'\A(:?//)?[^/.]+\.\w+', url):
        url = 'http://' + url.lstrip(':/')
        parsed = urlparse.urlsplit(url)
    
    # Lowercase scheme + domain
    parsed = list(parsed)
    parsed = map(str.lower, parsed[0:2]) + parsed[2:]
    url = urlparse.urlunsplit(parsed)
    
    return url



class Resource(object):
    
    def __init__(self, url):
        self.url = url
    
    @property
    def url(self):
        """Get the resource's uniform resource locator (URL)"""
        if not hasattr(self, '_url'):
            self._url = None
        return self._url
    
    @url.setter
    def url(self, new_url):
        """Set the resource's locator"""
        if not self.url == new_url:
            self._url = new_url
            del self.response
    
    @property
    def response(self):
        """Get the request.Response object for the resource"""
        if not hasattr(self, '_response') or not self._response:
            self._response = session.get(self.url)
        return self._response
    
    @response.setter
    def response(self, new_response):
        """Set the resource's response object"""
        self._response = new_response
    
    @response.deleter
    def response(self):
        """Reset the response object"""
        if hasattr(self, '_response'):
            del self._response
    
    def get_contents(self):
        return self.response.text
    
    def get_contents_as_file(self):
        return StringIO(self.get_contents())
    

if __name__ == "__main__":
   url = sys.argv[1]
   print Resource(url).get_contents()
