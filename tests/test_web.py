#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''Unit test for web.py

Tests the class for the intermediate interface
to access web pages.
'''

import unittest
import time

from shoplift.web import Resource, sanitize_url



class SanitizeURL(unittest.TestCase):
    """test sanitize_url functionality"""
    
    def testLeadingTrailingWhitespace(self):
        """sanitize_url should strip all surrounding whitespace"""
        testcases = (
            ('  http://example.com', 'http://example.com'),
            ('http://example.com    ', 'http://example.com'),
            ('	 http://example.com ', 'http://example.com'),
            ('http://example.com/space in between/', 'http://example.com/space in between/'),
            ('  http://example.com/space in between/  ', 'http://example.com/space in between/'),
            ('http://example.com', 'http://example.com'),
        )
        for testcase, expected_result in testcases:
            self.assertEqual(sanitize_url(testcase), expected_result)
    
    def testMissingScheme(self):
        """sanitize_url should auto-prefix http:// if the scheme is missing"""
        testcases = (
            ('example.com', 'http://example.com'),
            ('//example.com', 'http://example.com'),
            ('example.com//', 'http://example.com//'),
            ('//example.com//', 'http://example.com//'),
            ('//example.com/http://', 'http://example.com/http://'),
            ('http.com/', 'http://http.com/'),
            ('://httpbin.org', 'http://httpbin.org'),
        )
        for testcase, expected_result in testcases:
            self.assertEqual(sanitize_url(testcase), expected_result)
    
    def testCaseSensitivity(self):
        """sanitize_url should lowercase scheme and domain names"""
        testcases = (
            ('http://example.com', 'http://example.com'),
            ('http://Example.com', 'http://example.com'),
            ('http://example.COM', 'http://example.com'),
            ('http://example.CO.IN', 'http://example.co.in'),
            ('HTTP://EXAMPLE.CO.IN', 'http://example.co.in'),
            ('HTTP://TWITTER.COM/MIRANJ', 'http://twitter.com/MIRANJ'),
            ('http://EXAMPLE.com/spacebetween/UNCHANGED', 'http://example.com/spacebetween/UNCHANGED'),
            ('http://example.com', 'http://example.com'),
        )
        for testcase, expected_result in testcases:
            self.assertEqual(sanitize_url(testcase), expected_result)
    
    def testInvalidCases(self):
        testcases = (
            ('/amazon.com', '/amazon.com'),
            ('just a string', 'just a string'),
            ('.hgignore', '.hgignore'),
            ('.tm.properties', '.tm.properties'),
            ('http://example.com', 'http://example.com'),
        )
        for testcase, expected_result in testcases:
            self.assertEqual(sanitize_url(testcase), expected_result)
    
    def testValidCases(self):
        testcases = (
            ('amazon.com', 'http://amazon.com'),
            ('HTTP://WWW.APPLE.co.IN/iPhone  ', 'http://www.apple.co.in/iPhone'),
            # path name
            ('  //miranj.in/blog/2011/sweet-spot ', 'http://miranj.in/blog/2011/sweet-spot'),
            # query string
            ('http://httpbin.org/response-headers?Content-Type=text/plain;%20charset=UTF-8&Server=httpbin', 'http://httpbin.org/response-headers?Content-Type=text/plain;%20charset=UTF-8&Server=httpbin'),
            # unicode
            (' ://ümlaut.coM ', 'http://ümlaut.com'),
            ('https://example.com', 'https://example.com'),
            ('ftp://example.com', 'ftp://example.com'),
        )
        for testcase, expected_result in testcases:
            self.assertEqual(sanitize_url(testcase), expected_result)



class GetURLCorrectness(unittest.TestCase):
    sample_urls = (
        'http://httpbin.org/get',
        'http://google.com',
        'http://www.flipkart.com/the-hobbit/p/itmdx5tngyzzpx2u?pid=DGBDG2GFJDGZVNZS&srno=b_15&ref=7ca275d0-da30-45c0-b46e-fc9d5bc28a71',
    )
    
    def testGetURLValue(self):
        """Resource.url should return the unmodified URL passed as an initialiser argument"""
        for url in self.sample_urls:
            crawler = Resource(url)
            self.assertEqual(crawler.url, url)



class GetContentCorrectness(unittest.TestCase):
    expected_content = (
        # Tuples of url & a string match in the response body
        ('http://httpbin.org/get', r'"Host": "httpbin\.org"'),
        ('http://google.com', r'<html'),
        ('http://www.google.co.in', r'<html'),
        ('http://www.flipkart.com/harry-potter-deathly-hallows-j-k/p/itmczzt5jt4bxuna', r'Harry Potter')
    )
    
    def testGetContentsValue(self):
        """get_contents should return the html content of the URL"""
        for url, match in self.expected_content:
            crawler = Resource(url)
            self.assertRegexpMatches(crawler.get_contents(), match)



class GetPropertyPersistence(object):
    """Generic abstract class for testing persistence of web.Resource properties"""
    sample_urls = [
        'http://httpbin.org/get', # Every call to this URL has a unique response body
        'http://google.com', # Returns a 302, and should have a unique body per call
    ]
    method = ''
    
    def testSubsequentCalls(self):
        """ 'method' should return the same result for subsequent calls"""
        for url in self.sample_urls:
            crawler = Resource(url)
            property = getattr(crawler, self.method)
            first_result = callable(property) and property() or property
            second_result = callable(property) and property() or getattr(crawler, self.method)
            self.assertEqual(first_result, second_result)
    
    def testMultipleCalls(self):
        """ 'method' should return the same result every time it is called"""
        for url in self.sample_urls:
            crawler = Resource(url)
            property = getattr(crawler, self.method)
            first_result = callable(property) and property() or property
            for x in xrange(10):
                self.assertEqual(
                    callable(property) and property() or getattr(crawler, self.method),
                    first_result
                )
    
    def testDelayedCalls(self):
        """ 'method' should return the same result even after a time delay"""
        for url in self.sample_urls:
            crawler = Resource(url)
            property = getattr(crawler, self.method)
            first_result = callable(property) and property() or property
            time.sleep(5)
            second_result = callable(property) and property() or getattr(crawler, self.method)
            self.assertEqual(first_result, second_result)
    

class GetURLPersistence(unittest.TestCase, GetPropertyPersistence):
    method = 'url'

class GetContentPersistence(unittest.TestCase, GetPropertyPersistence):
    method = 'get_contents'



if __name__ == '__main__':
    unittest.main()
