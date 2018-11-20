#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import sys

def regex_filter(string, pattern):
    """Returns the first pattern match in a string or None"""
    
    try:
        matches = re.search(pattern, string)
        return matches and matches.group(1) or None
    except IndexError:
        return matches.group(0)
    except TypeError:
        return None

if __name__ == "__main__":
    string = sys.argv[1]
    pattern = sys.argv[2]
    print regex_filter(string, pattern)
