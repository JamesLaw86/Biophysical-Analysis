# -*- coding: utf-8 -*-
"""
Unit tests for data_process.py

"""
import unittest
import numpy as np
import data_process


#Test Data. A Circular Dichroism Spectrum form the PCDDB
if __name__ == "__main__":
    with open('Rhomboid protease glpG.csv') as csvFile:
        data = csvFile.readlines()
        xdim_test = data[1].split(',')
        y_test = np.array(data[0].split(','), dtype = float)
        y_testMultiple = [y_test * i for i in range(1, 11)]


class NormaliseTestCase(unittest.TestCase):
    """Test case for normalisation"""
    def test_Normalise(self):
        normalised = data_process.normaliseArea(y_test)
        self.assertAlmostEqual(np.sum(np.abs(normalised)), 1)

class SetDataRangeTestCase(unittest.TestCase):
    """Test case for setting data range"""
    def test_SetDataRangeSingleArray(self):
        upper = 230.0
        lower = 195.0
        #if xdim_test[0] > xdim_test[-1]:
        #    lower =  230
        #    upper = 195
        y_data, x_dim = data_process.setDataRange(y_test, xdim_test, upper, lower)
        print(min(x_dim))
        self.assertTrue(max(x_dim) == upper and min(x_dim == lower))
        self.assertTrue(len(y_data) == len(x_dim))
    
    #def test_SetDataRangeMultiArray(self):
    #    upper = 230
    #    lower = 195
        
        
        
        
        

if __name__ == '__main__':
    unittest.main()