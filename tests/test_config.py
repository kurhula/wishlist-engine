#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import unittest
import ConfigParser
from textwrap import dedent
from StringIO import StringIO

from mock import MagicMock, patch

from shoplift.config import *
from shoplift.exceptions import ConfigDoesNotExistException

BASE_CONFIG_TESTFILE = os.path.join(os.path.dirname(__file__), 'test_config.ini')

# Final output after parsing amazon_config_testdata.ini file and contents
product_output = {
    'amazon': {
        CONFIG_KEY_URL: {
            CONFIG_KEY_DOMAINS: ['amazon', 'junglee'],
            CONFIG_KEY_PATHS: '/.*/dp/.*/.*',
        },
        'price':    { CONFIG_KEY_METHOD: 'amazon_api.price_and_currency' },
        'image_url':{ CONFIG_KEY_METHOD: 'amazon_api.large_image_url' },
        'name':     { CONFIG_KEY_METHOD: 'amazon_api.title' }
    }
}



class TestExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = Extractor(BASE_CONFIG_TESTFILE)
        self.maxDiff = None
        
        for name, config in self.extractor.platforms.iteritems():
            if name == 'flipkart':
                self.flipkart_platform = (name, config)
            elif name == 'amazon.com':
                self.amazon_platform =  (name, config)
            elif name == 'itunes':
                self.itunes_platform = (name, config)
            elif name == 'apple':
                self.apple_platform = (name, config)
    
    
    
    def testCommaSeparatedToList(self):
        '''Test for comma separated entities in the...
           config file and returns them as expected
        '''
        
        # Input data for testing comma separated domain and path names
        comma_separated_input = dedent("""
            [flipkart]
            url.domains = flipkart, flip.kart, flipkar.t, .flipkart, www.flipkart.com, flip-kart
            url.path = (.*/dp/.*/.8)|(/uaa/.*/.*/.*)|(/a/.*/.*)
        """)
        
        # Final result list of comma separated domain names
        comma_separated_output = {
            'flipkart': {
                CONFIG_KEY_URL: {
                    CONFIG_KEY_DOMAINS: [
                        'flipkart',
                        'flip.kart',
                        'flipkar.t',
                        '.flipkart',
                        'www.flipkart.com',
                        'flip-kart'
                    ],
                    CONFIG_KEY_PATHS: '(.*/dp/.*/.8)|(/uaa/.*/.*/.*)|(/a/.*/.*)'
                },
            }
        }
        
        comma_separated_ins_input = StringIO(comma_separated_input)
        extractor_comma = Extractor(comma_separated_ins_input)
        comma_to_list_product = extractor_comma.platforms
        self.assertEqual(comma_to_list_product, comma_separated_output)
        
        comma_separated_input0 = dedent("""
            [ebay]
            url.domains = ebay.com
            url.path = *.////\s([^abc])
        """)
        
        comma_separated_output0 = {
            'ebay': {
                CONFIG_KEY_URL: {
                    CONFIG_KEY_DOMAINS: ['ebay.com'],
                    CONFIG_KEY_PATHS: '*.////\s([^abc])'
                },
            }
        }
        
        comma_separated_ins_input0 = StringIO(comma_separated_input0)
        extractor_comma0 = Extractor(comma_separated_ins_input0)
        comma_to_list_product0 = extractor_comma0.platforms
        self.assertEqual(comma_to_list_product0, comma_separated_output0)
    
    
    
    def testConfigParserString(self):
        '''Test for config parser method in case...
           the input config is string
        '''
        
        # String testdata input
        string_input = dedent("""
            [amazon]
            url.path    = /.*/dp/.*/.*
            url.domains = amazon, junglee
            image_url   = amazon_api.large_image_url
            name        = amazon_api.title
            price       = amazon_api.price_and_currency
        """)
        string_ins_input = StringIO(string_input)
        
        extractor = Extractor(string_ins_input)
        string_config_output = extractor.platforms
        self.assertEqual(string_config_output, product_output)
    
    
    
    def testConfigParserFile(self):
        '''Test for parsing config file
        '''
        
        testfile_config = Extractor(os.path.join(os.path.dirname(__file__), 'amazon_config_testdata.ini'))
        testfile_output = testfile_config.platforms
        self.assertEqual(testfile_output, product_output)
    
    
    
    def testConfigParserFail(self):
        '''Test for failing in reading config file ...
           in case it is in invalid format or not present
        '''
        
        self.assertRaises(ConfigDoesNotExistException, Extractor, 'test.yaml')
            
    
    
    
    def testInvalidConfigKeyHandling(self):
        '''Test for exception handling in case of invalid keys
        
        The keys url.path and url.domains are required config
        for a platform. Platform configs where these are missing
        should be ignored
        '''
        
        cases = (
            (   # Invalid only
                dedent("""
                    [amazon]
                    domain = amaz.on
                    path = xyz
                """),
                {}
            ),
            (   # Invalid followed by valid
                dedent("""
                    [amaz.on]
                    domains = amaz.on
                    urlpath = xyz
                    
                    [amazon]
                    url.domains = amazon.com
                    url.path = xyz
                """),
                { 'amazon': { CONFIG_KEY_URL: {
                    CONFIG_KEY_DOMAINS: ['amazon.com'],
                    CONFIG_KEY_PATHS: 'xyz',
                }}}
            ),
            (   # 2 valids followed by an invalid
                dedent("""
                    [amazon]
                    url.domains = amazon.com
                    url.path = xyz
                    
                    [flipkart]
                    url.domains = flipkart.com
                    url.path = flipped
                    
                    [amaz.on]
                    domain = amaz.on
                    path = xyz
                """),
                {
                    'amazon': { CONFIG_KEY_URL: {
                        CONFIG_KEY_DOMAINS: ['amazon.com'],
                        CONFIG_KEY_PATHS: 'xyz',
                    }},
                    'flipkart': { CONFIG_KEY_URL : {
                        CONFIG_KEY_DOMAINS: ['flipkart.com'],
                        CONFIG_KEY_PATHS: 'flipped',
                    }}
                }
            ),
        )
        
        for testcase, expected_result in cases:
            self.assertDictEqual(Extractor(StringIO(testcase)).platforms, expected_result)
    
    
    
    def testValidGetPlatform(self):
        '''Testing different supported platforms 
        
        Test for valid url and then the result...
        i.e, returning supported platform for ...
        valid url
        '''
        
        platform = self.extractor.get_platform('http://www.amazon.com/Crosley-CR8005A-BL-Cruiser-Portable-Turntable/dp/B008P8ELAE/ref=sr_1_8?m=A21C4U5X700J66&s=aht&ie=UTF8&qid=1402383743&sr=1-8')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.amazon_platform)
        
        platform = self.extractor.get_platform('http://www.flipkart.com/dc-comics-printed-men-s-round-neck-t-shirt/p/itmdvgwnbbhpf9gu?pid=TSHDVGWHMMHHFNNE&srno=b_4&ref=d3ab4e88-53b7-4ed9-899a-1d5fc76c3514')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.flipkart_platform)
        
        platform = self.extractor.get_platform('flipkart.com/dc-comics-printed-men-s-round-neck-t-shirt/p/itmdvgwnbbhpf9gu?pid=TSHDVGWHMMHHFNNE&srno=b_4&ref=d3ab4e88-53b7-4ed9-899a-1d5fc76c3514')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.flipkart_platform)
        
        platform = self.extractor.get_platform('//www.amazon.com/Crosley-CR8005A-BL-Cruiser-Portable-Turntable/dp/B008P8ELAE/ref=sr_1_8?m=A21C4U5X700J66&s=aht&ie=UTF8&qid=1402383743&sr=1-8')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.amazon_platform)
        
        platform = self.extractor.get_platform('://itunes.apple.com/in/album/ar.rahman-hits/id872316282')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.itunes_platform)
        
        platform = self.extractor.get_platform('http://store.apple.com/us/buy-appletv/appletv')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.apple_platform)
        
        platform = self.extractor.get_platform('   http://store.apple.com/us/buy-appletv/appletv   ')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.apple_platform)
        
        platform = self.extractor.get_platform('http://www.flipkart.com/apple-16gb-ipad-mini-wi-fi/p/itmdwptvje38mfkh?pid=TABDFWGGVJZ4YHZM&srno=b_2&ref=bcc2c663-54f6-4155-a93c-bccfc62488f6')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.flipkart_platform)
        
        platform = self.extractor.get_platform('https://itunes.apple.com/in/album/maaloom-from-lekar-hum-deewana/id880141533')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.itunes_platform)
        
        platform = self.extractor.get_platform('http://store.apple.com/us/buy-ipad/ipad-air/64gb-silver-wifi?aid=www-k2-ipad+air+-+index-n%40p&cp=k2-ipad+air+-n%40p')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.apple_platform)
        
        platform = self.extractor.get_platform('http://www.amazon.com/Denon-AVR-E300-Channel-Networking-Receiver/dp/B00B7X2OV2/ref=lp_281056_1_3?s=tv&ie=UTF8&qid=1402390122&sr=1-3')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.amazon_platform)
        
        platform = self.extractor.get_platform('http://store.apple.com/us/product/HA895LL/A/nest-learning-thermostat-2nd-generation?fnode=a79a99869a5fd6441d07af7100325defd98d5dc502fac468a84ce72c63b91861ec5e707b1ca3af4fc9b7bfeb3ab050274397db7543a1712d5600fd3905eb4e682ad4682763d0908859bb31d02a930480fa862da590992c35f83d72c47a61e7831a1dea5a541bb02c5d84cc287e507189')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.apple_platform)
        
        platform = self.extractor.get_platform('http://www.flipkart.com/flippd-men-s-checkered-casual-shirt/p/itmdtsh62kgrczfw?ayuhs/p/ayush/ayush')
        self.assertIsNotNone(platform)
        self.assertEqual(platform, self.flipkart_platform)
        
        # Test for a path match in the query string
        query_test_extractor = Extractor(StringIO(dedent("""
            [example]
            url.domains = example.com
            url.path = id=\d+
        """)))
        query_test_platform = ('example', query_test_extractor.platforms['example'])
        query_test_url = 'http://example.com/something/in/the/path?query=string&id=345&nice'
        platform = query_test_extractor.get_platform(query_test_url)
        self.assertIsNotNone(platform)
        self.assertEqual(platform, query_test_platform)
    
    
    
    def testInvalidGetPlatform(self):
        '''Tests for Invalid url
        
        Checking the invalid urls and their return...
        value which should be None for invalid urls
        '''
        
        self.assertIsNone(self.extractor.get_platform('http://www.flipkart.com/mens-clothing/t-shirts/pr?p[]=facets.type[]=Round%2BNeck&p[]=sort:popularity&sid=2oq,s9b,j9y&facetOrder[]=type&otracker=ch_vn_tshirts_me_subcategory_Round%20Neck#jumpTo=0|15'))
        
        self.assertIsNone(self.extractor.get_platform('ayush'))
        
        self.assertIsNone(self.extractor.get_platform('/www.flipkart.com/puma-solid-men-s-round-neck-t-shirt/p/itmdvfxctgsrbrdx?pid=TSHDVFWXGRCE8GYF&srno=b_6&ref=1761106e-e0f8-4a44-9fda-be55939634c2'))
        
        self.assertIsNone(self.extractor.get_platform('http://www.amazon.com/s/'))
        
        self.assertIsNone(self.extractor.get_platform('https://www.apple.com/itunes/'))
        
        self.assertIsNone(self.extractor.get_platform(1234))
        
        self.assertIsNone(self.extractor.get_platform(str))
        
        self.assertIsNone(self.extractor.get_platform('tiwari.ayush2412@gmail.com'))
        
        self.assertIsNone(self.extractor.get_platform('http://www.amazon.com/puma-solid-men-s-round-neck-t-shirt/p/itmdvfxctgsrbrdx'))
        
        self.assertIsNone(self.extractor.get_platform('http://www.facebook.com/pink-floyd-printed-men-s-round-neck-t-shirt/p/itmdz46ubth869nz?pid=TSHDZ46T7QZGJSFS&srno=b_9&ref=040d98ab-ea8c-466d-86bb-f9bd5114231c'))
        
        self.assertIsNone(self.extractor.get_platform(''))
    
    
    
    def testExtract(self):
        '''Test for checking if the right function call is made or not
        
        Test for valid and invalid url that checks if the ...
        invoke_extraction_method is called or not
        '''
        
        ref = Extractor(BASE_CONFIG_TESTFILE)
        
        ref.invoke_extraction_method = MagicMock()
        ref.extract('http://www.flipkart.com/hanes-solid-men-s-round-neck-t-shirt/p/itmdu4rcb6awun7j?pid=TSHDU4RCKUZSCZ8B&srno=b_2&ref=6a37b3b1-9d4d-43b7-a40d-868d5b897308')
        self.assertTrue(ref.invoke_extraction_method.called)
        
        ref.invoke_extraction_method = MagicMock()
        ref.extract('http://store.apple.com/us/buy-ipad/ipad-air/64gb-silver-wifi?aid=www-k2-ipad+air+-+index-n%40p&cp=k2-ipad+air+-n%40p')
        self.assertTrue(ref.invoke_extraction_method.called)
        
        ref.invoke_extraction_method = MagicMock()
        ref.extract('http://www.facebook.com/pink-floyd-printed-men-s-round-neck-t-shirt/p/itmdz46ubth869nz?pid=TSHDZ46T7QZGJSFS&srno=b_9&ref=040d98ab-ea8c-466d-86bb-f9bd5114231c')
        self.assertFalse(ref.invoke_extraction_method.called)
        
        ref.invoke_extraction_method = MagicMock()
        ref.extract('//www.amazon.com/Crosley-CR8005A-BL-Cruiser-Portable-Turntable/dp/B008P8ELAE/ref=sr_1_8?m=A21C4U5X700J66&s=aht&ie=UTF8&qid=1402383743&sr=1-8')
        self.assertTrue(ref.invoke_extraction_method.called)
        
        ref.get_platform = MagicMock()
        ref.extract('http://store.apple.com/us/buy-ipad/ipad-air/64gb-silver-wifi?aid=www-k2-ipad+air+-+index-n%40p&cp=k2-ipad+air+-n%40p')
        ref.get_platform.assert_called_once_with('http://store.apple.com/us/buy-ipad/ipad-air/64gb-silver-wifi?aid=www-k2-ipad+air+-+index-n%40p&cp=k2-ipad+air+-n%40p')
    
    
    
    @patch('shoplift.scrapers.opengraph')
    def testinvoke_opengraph(self, mock_opengraph):
        '''Test for invoke_extraction call
        
        Test that checks if the correct scraper method has ...
        called or not
        '''
        
        ext = Extractor(BASE_CONFIG_TESTFILE)
        ext.invoke_extraction_method({ 'method': 'opengraph.title' }, 'http://www.flipkart.com/hanes-solid-men-s-round-neck-t-shirt/p/itmdu4rcb6awun7j?pid=TSHDU4RCKUZSCZ8B&srno=b_2&ref=6a37b3b1-9d4d-43b7-a40d-868d5b897308')
        mock_opengraph.assert_called_with('http://www.flipkart.com/hanes-solid-men-s-round-neck-t-shirt/p/itmdu4rcb6awun7j?pid=TSHDU4RCKUZSCZ8B&srno=b_2&ref=6a37b3b1-9d4d-43b7-a40d-868d5b897308', 'title')
    
    
    
    @patch('shoplift.filters.regex')
    @patch('shoplift.scrapers.microdata')
    def testinvoke_regex(self, mock_microdata, mock_regex):
        '''Test for checking filter call'''
        
        ext = Extractor(BASE_CONFIG_TESTFILE)
        ext.invoke_extraction_method({ 'method': 'microdata.name', 'filter': 'regex.abc' }, 'ayush')
        mock_microdata.assert_called_with('ayush', 'name')
        mock_microdata.return_value = 'xyz'
        ext.invoke_extraction_method({ 'method': 'microdata.name', 'filter': 'regex.abc' }, 'ayush')
        mock_regex.assert_called_with('xyz', 'abc')
    
    
    
    @patch('shoplift.filters.tuple')
    @patch('shoplift.scrapers.xpath')
    def testinvoke_tuple(self, mock_xpath, mock_tuple):
        '''Test for checking tuple filter call'''
        
        ext = Extractor(BASE_CONFIG_TESTFILE)
        ext.invoke_extraction_method({ 'method': 'xpath.ay/asa*/c.*', 'filter': 'tuple.0' }, 'any_url')
        mock_xpath.assert_called_with('any_url', 'ay/asa*/c.*')
        mock_xpath.return_value = ('ayush', 123)
        ext.invoke_extraction_method({ 'method': 'xpath.ay/asa*/c.*', 'filter': 'tuple.0' }, 'any_url')
        mock_tuple.assert_called_with(('ayush', 123), '0')



if __name__ == "__main__":
    unittest.main()
