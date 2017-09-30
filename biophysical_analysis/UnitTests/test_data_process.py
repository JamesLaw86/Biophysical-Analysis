# -*- coding: utf-8 -*-
"""
Unit tests for data_process.py

"""
import unittest
import numpy as np
import data_process


"""Test Data. A Circular Dichroism Spectrum form the PCDDB. Molecule 
    of the month September 2017!!"""
if __name__ == "__main__":
    with open('Rhomboid protease glpG.csv') as csvFile:
        data = csvFile.readlines()
        xdim_test = data[1].split(',')
        y_test = np.array(data[0].split(','), dtype = float)
        y_testMultiple = [y_test * i for i in range(1, 11)]


class NormaliseTestCase(unittest.TestCase):
    """Test case for normalisation. Ensure normalised data sums to 1"""
    def test_Normalise(self):
        normalised = data_process.normaliseArea(y_test)
        self.assertAlmostEqual(np.sum(np.abs(normalised)), 1)

class SetDataRangeTestCase(unittest.TestCase):
    """
    Test case for setting data range.
    """
    def setUp(self):
        """Range to cut data"""
        self.upper = 230.0
        self.lower = 195.0
        
    def test_SetDataRangeSingleArray(self):
        """
        Ensure new wavelegnth range is correct and that new y_data has the 
        same length.
        """
        y_data, x_dim = data_process.setDataRange(y_test, xdim_test,
                                                  self.upper, self.lower)
        self.assertTrue(x_dim[-1] == self.lower and x_dim[0] == self.upper)
        self.assertTrue(len(y_data) == len(x_dim))
    
    def test_SetDataRangeMultiArray(self):
        """As above for multiple arrays of data.""" 
        y_multiData, x_dim = data_process.setDataRange(y_testMultiple, xdim_test, 
                                                       self.upper, self.lower)
        self.assertTrue(x_dim[-1] == self.lower and x_dim[0] == self.upper)
        for spectrum in y_multiData:
            self.assertTrue(len(spectrum) == len(x_dim))

class thinDataTest(unittest.TestCase):
    """Test case for data thinning."""
    def setUp(self):
       """Factors by which to reduce data step."""
       self.splits = (2,3,4)
        
    def test_ThinData(self):
        """
        Checks the wavelegth step is reduced by appropriate factor and
        new y_data has the same length as the new x_axis.
        """
        for split in self.splits:
            y_data, x_data = data_process.thinData(y_test, xdim_test, split)
            oldStep = float(xdim_test[1]) - float(xdim_test[0])
            newStep = float(x_data[1]) - float(x_data[0])
            self.assertAlmostEqual(newStep/oldStep,split)
            self.assertTrue(len(y_data) == len(x_data))
            
    def test_ThinDataMultiArray(self):
        """As above for multiple arrays of data."""
        for split in self.splits:
            y_data, x_data = data_process.thinData(y_testMultiple, xdim_test, split)
            for spec in y_data:
                self.assertTrue(len(spec) == len(x_data))


class barycentricMeanTest(unittest.TestCase):
    """
    Basic test for barycentric mean calculation.
    Checks that a 180 degree sine wave gives a result of 90 degrees
    """
    def setUp(self):
        self.array = np.linspace(0, np.pi ,10000)
        self.sin_wave = np.sin(self.array)
        
    def test_BarycentricMean(self):
        bcm = data_process.baryCentricMean(self.sin_wave, self.array)
        self.assertAlmostEqual(bcm, np.pi/2)


if __name__ == '__main__':
    unittest.main()