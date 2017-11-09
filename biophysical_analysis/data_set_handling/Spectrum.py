# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 08:10:20 2017

@author: james.law
"""

import xy_dataSet

class Spectrum(xy_dataSet.xy_dataSet):
    """
    Class to hold an x-y Spectrum. Can be instantiated directly with raw data
    or using the class methods to read various dataformats (i.e. csv, JCamp).
    
    **kwargs are remarks or settings related to the dataset which are read in
    automatically if using one of the above dataformats. From kwargs we extract 
    the JCamp defined properties TITLE, XUNITS, YUNITS to define the name, and
    y and x- axis units and are read in as member variables. Remaining settings
    make up a member variable (dict) called 'remarks'."""
    
    
    def __init__(self):
        pass
    
    def normaliseArea(area = 1)