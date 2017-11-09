# -*- coding: utf-8 -*-
"""

A class to hold an x-y spectrum

"""
import numpy as np
import sys
import re
from DataSetHandling import JCamp_DataSet_Reader as JCampReader
from DataSetHandling import CSV_Dataset_Reader as csvR

if __name__ == '__main__':
    sys.path.append('../')
    
from DataProcessing import data_process

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
        #Now check x and y arrays are the same size!
        len_x = len(self.x_axis)
        len_y = len(self.y_data)
        if len_x != len_y:
            msg = 'Length of x_axis ({}) not equal to y_axis ({})'
            msg = msg.format(len_x, len_y)
            raise ValueError(msg)
        
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

#JCampSpec = Spectrum.setupJCamp('jcampTest.jdx')
#csvSpec = Spectrum.setupCSV('HorizontalDataSet.csv', orientation = 'Horizontal')

















