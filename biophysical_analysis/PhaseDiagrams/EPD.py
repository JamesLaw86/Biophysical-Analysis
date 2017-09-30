# -*- coding: utf-8 -*-
"""
This will be a class for creating Empirical Phase Diagrams (EPDs)
See "Maddux, N. R., Joshi, S. B., Volkin, D. B., Ralston, J. P., & Middaugh, C. R. (2011). 
Multidimensional methods for the formulation of biopharmaceuticals and vaccines. 
Journal of Pharmaceutical Sciences, 100(10), 4171–4197. https://doi.org/10.1002/jps.22618 

"""

import sys
sys.path.append('../')
from DataProcessing import data_process
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class EPD(object):
    """
    Will contain the EPD data and plot. The plot will be a matplotlib figure 
    which is a member of the class. 
    """
    def __init__(self, excelFiles, x_axis):
        """
        data files are excel documents laid out in the very specific
        format yet to be defined! x_axis must be in the same order as
        the files
        """
        try:
            self.setupData(self, excelFiles, x_axis)
        except:
            print("Data couldn't be set up, check data formats")
        
        
    def setupData(self, excelFiles, x_axis):
        pass
    


