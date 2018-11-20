#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import sys
import ConfigParser
import urlparse

from . import scrapers, filters
from .web import sanitize_url, Resource
from .exceptions import ConfigDoesNotExistException

# Assigning var names to hard-coded strings
CONFIG_KEY_METHOD = 'method'
CONFIG_KEY_URL = 'url'
CONFIG_KEY_PATHS = 'path'
CONFIG_KEY_DOMAINS = 'domains'
CONFIG_KEY_FILTER = 'filter'
CONFIG_KEY_SEPARATOR = '.'

class Extractor:
    '''
        Extractor that returns the product info given the url of
        the product page of the valid e-commerce websites
    '''
    
    def __init__(self, config_file):
        """Initializes the url passed by the user"""
        
        self.platforms = {}
        self.config_file = config_file
        self.parse_config()
    
    def parse_config(self):
        """Parses the config file
        
        Parses the file using ConfigParser and saves the
        values in self.platforms
        """
        
        config_file = self.config_file
        
        # Try reading `config_file` if it isn't already a file or file-like object
        if not hasattr(config_file, 'readline'):
            if not os.path.exists(config_file):
                    raise ConfigDoesNotExistException
            
            config_file = open(config_file, 'r')
        
        Config = ConfigParser.ConfigParser()
        Config.readfp(config_file)
        config_file.close()
        
        # Extract the contents of config_file
        platforms = {
            name: dict(Config.items(name))
            for name in Config.sections()
        }
        
        # Sanitize data
        platforms = {
            name: {
                # Append missing '.method' default suffix to config items
                CONFIG_KEY_SEPARATOR in key and key or key + CONFIG_KEY_SEPARATOR + CONFIG_KEY_METHOD : value
                for key, value in config.iteritems()
            }
            for name, config in platforms.iteritems()
            
            # Ignore platforms with an incomplete configuration
            if all ('%s.%s' % (CONFIG_KEY_URL, k) in config for k in (CONFIG_KEY_DOMAINS,CONFIG_KEY_PATHS))
        }
        
        # Re-structure data
        self.platforms = {}
        for name, config in platforms.iteritems():
            
            # Split keys by '.' and create nested dictionaries
            new_config = {}
            for key, value in config.iteritems():
                parent, child = key.split(CONFIG_KEY_SEPARATOR, 1)
                if parent not in new_config : new_config[parent] = {}
                new_config[parent][child] = value
            config = new_config
            
            # Change url.domains from csv to a list
            config[CONFIG_KEY_URL][CONFIG_KEY_DOMAINS] = map(str.strip, config[CONFIG_KEY_URL][CONFIG_KEY_DOMAINS].split(','))
            self.platforms[name] = config
        
    
    def extract(self, url):
        """Return the product info found at the given URL
        
        Returns a dictionary with items: name, image, price, currency
        """
        
        product = {}
        resource = Resource(url)
        platform = self.get_platform(resource.url)
        
        # Extract individual attributes based on the config
        if platform and len(platform) == 2:
            name, config = platform
            for attribute, method in config.iteritems():
                product[attribute] = self.invoke_extraction_method(method, resource)
        
        return product
    
    def get_platform(self, url):
        """Gets the supported platform for a given URL
        
        Checks for a matching URL config and, if found, 
        returns a tuple with the platform name & attributes config:
        (<name>, { <attr> : { <key> : <method>'.'<arg> }})
        """
        
        url = urlparse.urlsplit(sanitize_url(url))
        
        # Find the first platform config that matches the URL criteria
        for name, config in self.platforms.iteritems():
            if len(filter(
                # Check for a url.domain match
                url.netloc.endswith,
                config[CONFIG_KEY_URL][CONFIG_KEY_DOMAINS]
                
            )) and re.search(
                # Search for a url.path match
                r'%s' % config[CONFIG_KEY_URL][CONFIG_KEY_PATHS],
                # Reconstruct the URL from the path onwards
                urlparse.urlunsplit(('','') + url[2:])
            ):
                return (name, config)
            
        return None
    
    def invoke_extraction_method(self, config, url):
        """Invokes a list of functions and returns the final result
        
        Expects the list of functions in the following dict format
        { # <key>    : <function_name>'.'<function_argument>,
            'method' : 'microdata./properties/offers/0/properties/price/0',
            'filter' : 'regex.(\\d+.\\d+)',
        }
        """
        
        call_order = (
            (CONFIG_KEY_METHOD, scrapers),
            (CONFIG_KEY_FILTER, filters),
        )
        
        # Iterate over the call_order, and reduce from left to right
        # to get the final result
        result = url
        for key, module in call_order:
            if key in config:
                function, arg = config[key].split(CONFIG_KEY_SEPARATOR, 1)
                if callable( getattr(module, function, None) ):
                    result = getattr(module, function)(result, arg)
        
        return isinstance(result, Resource) and result.url or result



if __name__ == '__main__' and len(sys.argv) >= 2:
    # For command line call
    url = sys.argv[1]
    # Command line function call by calling extration method
    extractor_instance = Extractor('shoplift/config.ini')
    print extractor_instance.extract(url)
