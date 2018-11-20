#!/usr/bin/env python
# -*- coding: UTF-8 -*-

def tuple_filter(tuple_obj, index):
    """Returns tuple value at the given index"""
    
    # Force typecast index into integer
    try:
        index = int(index)
    except ValueError:
        return None
    
    # Verify if tuple_obj is a tuple
    if isinstance(tuple_obj, tuple):
        try:
            return tuple_obj[index]
        except IndexError:
            return None
    else:
        return None
