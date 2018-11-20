#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from shoplift.filters import *



class TestFilters(unittest.TestCase):
    
    def testRegexFilter(self):
        """Test regex filter behaviour"""
        
        # Test matches
        
        self.assertEqual(regex('abcde', 'abcde'), 'abcde')
        
        self.assertEqual(regex('abcde', '(abcde)'), 'abcde')
        
        self.assertEqual(regex('abcde', '(abc)de'), 'abc')
        
        self.assertEqual(regex('abcde', '(a)bc(d)e'), 'a')
        
        self.assertEqual(regex('ayush2413', '(\d+.\d+)'), '2413')
        
        self.assertEqual(regex('USD 23.45', '(\d+.\d+)'), '23.45')
        
        self.assertEqual(regex('ayush1234567', '(\d+.\d+)|(abc.*)'), '1234567')
        
        # Test empty match
        
        self.assertEqual(regex('abcde', ''), '')
        
        # Test no match
        
        self.assertIsNone(regex('ayush2413', '(\d+\.\d+)'))
        
        self.assertIsNone(regex('', '(\d+.\d+)'), '')
        
        self.assertIsNone(regex('hoola', '(\d+.\d+)'))
        
        self.assertIsNone(regex('abcde', '/(a)bc(f)e/'))
        
        self.assertIsNone(regex('abcde', 'abcdef'))
        
        self.assertIsNone(regex(None, ''))
    
    
    def testTupleFilter(self):
        """Test tuple filter behaviour"""
        
        # Test valid indexes
        
        self.assertEqual(tuple_filter(('USD',123), 0), 'USD')
        
        self.assertEqual(tuple_filter(('USD',123), -2), 'USD')
        
        self.assertEqual(tuple_filter(('USD',123), 1), 123)
        
        self.assertEqual(tuple_filter(('USD',123), -1), 123)
        
        # Test invalid cases
        
        self.assertIsNone(tuple_filter(('USD',123), 2))
        
        self.assertIsNone(tuple_filter('a random string', 3))
        
        self.assertIsNone(tuple_filter(None, 0))
        
        self.assertRaises(TypeError, tuple_filter('', ''))



if __name__ == "__main__":
    unittest.main()
