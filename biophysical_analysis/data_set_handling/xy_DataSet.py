# -*- coding: utf-8 -*-
"""

A class to hold an x-y spectrum

"""
import numpy as np
import sys
import re
import scipy.signal
import time

if __name__ == '__main__':
    sys.path.append('../')
    
from data_set_handling import JCamp_DataSet_Reader as JCampReader
from data_set_handling import CSV_Dataset_Reader as csvR
from data_processing import data_process as dp

class xy_dataSet(object):
    """
    Class to hold an x-y data set. Can be instantiated directly with raw data
    or using the class methods to read various dataformats (i.e. csv, JCamp).
    
    **kwargs are remarks or settings related to the dataset which are read in
    automatically if using one of the above dataformats. From kwargs we extract 
    the JCamp defined properties TITLE, XUNITS, YUNITS to define the name, and
    y and x- axis units and are read in as member variables. Remaining settings
    make up a member variable (dict) called 'remarks'.
    
    """
    def __init__(self, x_axis = None, y_data = None, dataType = float, **kwargs):
        self.y_data = np.array(y_data, dtype = dataType)
        self.x_axis = np.array(x_axis, dtype = dataType)
        self.__checkArrayDims()
        self.original_y_data = self.y_data.copy()
        self.original_x_axis = self.x_axis.copy()
        self.x_units, self.y_units = None, None
        self.remarks = {}
        self.Title = ""
        self.modifications = {}
        self.results = {}
        self.__setInitialLabels(kwargs)
    
    def __setInitialLabels(self, labels):
        """
        Extract x y units and title from the kwargs passed 
        to constructor. All other entries go into self.remarks
        """
        for key, value in labels.items():
            if key == 'YUNITS':
                self.y_units = value
            elif key == 'XUNITS':
                self.x_units = value
            elif key == 'TITLE':
                self.Title = value
            else:
                self.remarks[key] = value
    
    
    @classmethod
    def setupJCamp(cls, file, y_column = 1):
        """
        Sets up from a JCAMP-DX: "The joint Committee on Atomic and 
        Molecular Physical data – Data Exchange format."
        y_column refers to the y data column that is read in.
        """
        JCampSpec = JCampReader.JCampReader(file, y_column)
        x_axis = JCampSpec.xy_data[0]
        y_data = JCampSpec.xy_data[1]
        remarks = JCampSpec.remarks
        return cls(x_axis, y_data, **remarks)
    
    @classmethod
    def setupCSV(cls, file, orientation = 'Vertical', y_column = 1):
        """
        Sets up spectrum from a csv file.
        y_column refers to the y data column that is read in.
        """
        csvSpec = csvR.csvSpecReader(file, y_column, orientation)
        x_axis = csvSpec.xy_data[0]
        y_data = csvSpec.xy_data[1]
        remarks = csvSpec.remarks
        return cls(x_axis, y_data, **remarks)
        
    def __checkArrayDims(self):
        """Ensures spectrum array dimensions make sense"""
        if self.x_axis.ndim > 1:
            raise ValueError('Multidimensional x_axis not supported for 2d Spectrum!!')
        if self.y_data.ndim > 1:
            self.y_axis = np.average(self.y_axis, 0)
            print('Warning, y_data was multidimensional and has been avergaed!!')
        #Check x and y arrays are the same size!
        len_x = len(self.x_axis)
        len_y = len(self.y_data)
        if len_x != len_y:
            msg = 'Length of x_axis ({}) not equal to y_axis ({})'
            msg = msg.format(len_x, len_y)
            raise ValueError(msg)
    
    def reset(self):
        """Resets to the orginal x-y arrays that were read in"""
        self.x_axis =  self.original_x_axis
        self.y_axis = self.original_y_data
        self.modifications['DataReset':time.localtime()]
        
    def addResult(self, resultKey, result):
        """
        Adds result to self.results. For a given resultKey, results are indexed in
        order they were added. 
        """
        if not resultKey in self.results:
            self.results[resultKey] = {0 : result, 'count': 1}
            return
        n = self.results[resultKey]['count']
        self.results[resultKey][n + 1] = result
        self.results[resultKey]['count'] += 1
        
    def set_xrange(self, lower, upper):
        """Set the plot limits of the x-axis"""
        try:
            self.x_axis, self.y_data = dp.setDataRange(self.original_x_axis,
                                                       self.original_y_data,
                                                       lower, upper)
        except ValueError as e:
            print("Data range couldn't be changed so hasn't been", e)
            return
        self.modifications['Range_Change'] =  {'Lower':str(lower),
                                               'Upper':str(upper), 
                                               'Time':time.localtime()}
    
    def thin_data(self, reductionFactor = 2, startIndex = 0):
        """
         Reduces the number of data points by a factor of "reductionFactor"
         This is useful when we are working with datasets with different steps.
         StartIndex defines where we start the thinning.
        """
        try:
            self.x_units, self.y_data = dp.thinData(self.y_data, self.x_axis,
                                                    reductionFactor, startIndex)
        except ValueError as e:
            print('Data couldn\'t be thinned so hasn\'t been.', e)
            return
        mod = {'ReducedByFactorOf': reductionFactor, 'Started@Index':startIndex,
               'Time': time.localtime()}
        self.modifications.setdefault('Thinning', []).append(mod)
        
        
    def smooth(self, window = 7, polyorder = 3):
        """
        Uses the savitsy golay algorithm in scipy.signal to smooth
        the spectrum
        """
        self.y_data = scipy.signal.savgol_filter(self.y_data, window, polyorder)
        mod = {'window':window, 'polyorder':polyorder, 'Time':time.localtime()}
        self.modifications.setdefault('Smoothing', []).append(mod)
        
    def derivative(self, n = 1, window = 7, polyorder = 3):
        """
        Uses the savitsy golay algorithm in scipy.signal. Returns an array
        of the processed data.
        """
        return scipy.signal.savgol_filter(self.y_data, window, polyorder, deriv = n)
        
    
        

