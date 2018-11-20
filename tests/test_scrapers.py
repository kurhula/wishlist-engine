#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''Unit tests for shoplift.scrapers

Test the scraping APIs exposed by the different
scraping methods.
'''

import unittest

from shoplift.web import Resource
from shoplift.scrapers import *



class TestScrapers(unittest.TestCase):
    
    def testResourceInputSupport(self):
        """web.Resource objects should be supported as input"""
        
        testcases = (
            (
                amazon_api,
                'http://www.amazon.com/Harry-Potter-Sorcerers-Stone-Book/dp/059035342X/ref=sr_1_1?s=books&ie=UTF8&qid=1403099669&sr=1-1&keywords=harry+potter',
                'title',
                r"Harry Potter and the Sorcerer's Stone \(Harry Potters\)",
            ),
            (
                microdata,
                'http://www.flipkart.com/the-hobbit/p/itmdx5tngyzzpx2u?pid=DGBDG2GFJDGZVNZS&srno=b_15&ref=7ca275d0-da30-45c0-b46e-fc9d5bc28a71',
                '/properties/name/0',
                r"The Hobbit",
            ),
            (
                opengraph,
                'https://itunes.apple.com/in/album/songs-innocence-deluxe-edition/id928428096',
                'title',
                r"Songs of Innocence \(Deluxe Edition\) by U2"
            ),
            (
                xpath,
                'http://example.com',
                '//h1//text()',
                r"Example Domain",
            )
        )
        
        for scraper_method, url, key, expected in testcases:
            try:
                result = scraper_method(Resource(url), key)
            except Exception as e:
                self.fail(scraper_method.__name__ + " unexpectedly raised an exception")
            else:
                self.assertIsNotNone(result, scraper_method.__name__ + " unexpectedly returned None")
                self.assertRegexpMatches(result, expected)
    
    
    
    def testAmazonApiScraper(self):
        '''Test for amazon API scraping'''
        
        self.assertEqual(amazon_api('avcd', ''), None)
        
        self.assertEqual(amazon_api(1234, ''), None)
        
        self.assertEqual(amazon_api('', 'ayush'), None)
        
        self.assertEqual(amazon_api('http://www.amazon.com/Harry-Potter-Sorcerers-Stone-Book/dp/059035342X/ref=sr_1_1?s=books&ie=UTF8&qid=1403099669&sr=1-1&keywords=harry+potter', 'title'), "Harry Potter and the Sorcerer's Stone (Harry Potters)")
        
        self.assertEqual(amazon_api('http://www.amazon.com/Harry-Potter-Sorcerers-Stone-Book/dp/059035342X', 'title'), "Harry Potter and the Sorcerer's Stone (Harry Potters)")
        
        self.assertEqual(amazon_api('http://www.amazon.com/Harry-Potter-Sorcerers-Stone-Book/dp/059035342X/ref=sr_1_1?s=books&ie=UTF8&qid=1403099669&sr=1-1&keywords=harry+potter', 'rate'), None)
        
        self.assertEqual(amazon_api('http://www.amazon.com/Harry-Potter-Sorcerers-Stone-Book/dp/059035342X/?ayush=ayush', 'title'), "Harry Potter and the Sorcerer's Stone (Harry Potters)")
        
        self.assertEqual(amazon_api('ayush/dp/ayush', 'title'), None)
        
        self.assertEqual(amazon_api('', ''), None)
        
        self.assertEqual(amazon_api('http://www.flipkart.com/flippd-men-s-checkered-casual-shirt/p/itmdtsh62kgrczfw', 'title'), None)
    
    
    
    def testMicrodataScraper(self):
        '''Test for microdata_scraper module
        
        Checking the expected results of microdata...
        scraping for cached web-pages
        '''
        
        self.assertEqual(microdata('http://www.flipkart.com/the-hobbit/p/itmdx5tngyzzpx2u?pid=DGBDG2GFJDGZVNZS&srno=b_15&ref=7ca275d0-da30-45c0-b46e-fc9d5bc28a71', '/properties/name/0').strip(), "The Hobbit")
        
        self.assertEqual(microdata('http://www.flipkart.com/the-hobbit/p/itmdx5tngyzzpx2u?pid=DGBDG2GFJDGZVNZS&srno=b_15&ref=7ca275d0-da30-45c0-b46e-fc9d5bc28a71', 123), None)
        
        self.assertEqual(microdata('https://itunes.apple.com/in/album/songs-innocence-deluxe-edition/id928428096', 'name'), None)
        
        self.assertEqual(microdata('', '/properties/name/0'), None)
        
        self.assertEqual(microdata('http://www.flipkart.com/the-hobbit/p/itmdx5tngyzzpx2u?pid=DGBDG2GFJDGZVNZS&srno=b_15&ref=7ca275d0-da30-45c0-b46e-fc9d5bc28a71', '/properties/name/0').strip(), "The Hobbit")
        
        self.assertEqual(microdata('', ''), None)
        
        self.assertEqual(microdata('ayush', 'ayush'), None)
        
        self.assertEqual(microdata(1234, ''), None)
        
        self.assertEqual(microdata('', 1234), None)
    
    
    
    def testXpathScraper(self):
        '''Test for xpath_scraper module
        
        Testing the expected output of xpath ...
        scraping for cached web-pages
        '''
        
        self.assertEqual(xpath('https://itunes.apple.com/in/album/songs-innocence-deluxe-edition/id928428096','//div[@class="callout"]/div[@class="left"]//text()'), 'iTunes')
        
        self.assertEqual(xpath('https://itunes.apple.com/in/album/songs-innocence-deluxe-edition/id928428096', 'a_string'), None)
        
        self.assertEqual(xpath('https://itunes.apple.com/in/album/songs-innocence-deluxe-edition/id928428096', '/ayush'), None)
        
        self.assertEqual(xpath('', ''), None)
        
        self.assertEqual(xpath(1234, ''), None)
        
        self.assertEqual(xpath('ayush', '//span'), None)
        
        self.assertEqual(xpath('google.com', '*ayush*'), None)
        
        self.assertEqual(xpath('google.com', ''), None)
    
    
    
    def testOpenGraphScraper(self):
        '''Test for opengraph_scraper module 
        
        Test the expected output for open_graph scraping ...
        for cached web-pages
        '''
        self.assertEqual(opengraph('https://itunes.apple.com/in/album/songs-innocence-deluxe-edition/id928428096', 'title'), "Songs of Innocence (Deluxe Edition) by U2")
        
        self.assertEqual(opengraph('https://itunes.apple.com/in/album/songs-innocence-deluxe-edition/id928428096', ''), None)
        
        self.assertEqual(opengraph('https://itunes.apple.com/us/album/overexposed/id536292140', 'a_string'), None)
        
        self.assertEqual(opengraph('', ''), None)
        
        self.assertEqual(opengraph('string', 1234), None)
        
        self.assertEqual(opengraph('string', ''), None)



if __name__ == "__main__":
    unittest.main()
