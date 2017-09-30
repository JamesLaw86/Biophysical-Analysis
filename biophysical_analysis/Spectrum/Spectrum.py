# -*- coding: utf-8 -*-
"""

A class to hold an x-y spectrum

"""

import numpy as np
import sys

if __name__ == '__main__':
    sys.path.append('../')
    
from DataProcessing import data_process

class Spectrum(object):
    def __init__(self, y_data = None, x_axis = None, remarks = None):
        self.y_data, self.original_y_data = y_data
        self.x_axis, self.original_x_axis = x_axis
        self.remarks = remarks
    
    @classmethod
    def setupJCamp(cls, file):
        """
        Sets up from a JCAMP-DX: "The joint Committee on Atomic and 
        Molecular Physical data – Data Exchange format"
        """
        
        return cls()
                
    #@classmethod