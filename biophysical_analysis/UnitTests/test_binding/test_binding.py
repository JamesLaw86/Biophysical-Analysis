# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 17:46:09 2017

@author: james.law
"""

import unittest
import numpy as np
import sys
import os

path = os.getcwd()
if __name__ == '__main__':
    newPath = path.split('UnitTests')[0]
    sys.path.append(newPath)
    
from Binding import titration_dataset

class BimolSimpTestCase(unittest.TestCase):
    """Test the simple Bimolecular binding fitting function"""
    data_set = titration_dataset.binding_dataset.setupCSV("Binding Dataset.csv")
    #print(data_set.x_axis)
    #print(data_set.y_data)
    print(data_set.x_axis)

if __name__ == '__main__':
    unittest.main()
    



#class NormaliseTestCase(unittest.TestCase):
#    """Test case for normalisation. Ensure normalised data sums to 1"""
#    def test_Normalise(self):
#        normalised = data_process.normaliseArea(y_test)
#        self.assertAlmostEqual(np.sum(np.abs(normalised)), 1)
