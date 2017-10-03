# -*- coding: utf-8 -*-
"""
Class for reading JCamp Spectrum files. 

"""

import re

class JCampReader(object):
    """
    Reads from a JCAMP-DX: "The joint Committee on Atomic and 
    Molecular Physical data – Data Exchange format. 
    X-Y data is held in variable xy_data. Index 1 contains x axis
    and remaining y-axis spectra are subsequent indexes.
    
    Constructor takes keyword 'y_colums' which should be an list
    or tuple of the columns starting with index 1. That is
    (1,4) will extract the 1st and 4th columns of y_data 
    
    """
    def __init__(self, file, y_columns = 'All'):
        with open(file, 'r') as jcampFile:
            spectrumData = jcampFile.readlines()
        try:
            lineNumber, self.remarks = self.__readRemarks(spectrumData)
            self.xy_data = self.__get_xy_data(spectrumData, lineNumber, y_columns)
        except ValueError as e:
            print(e.message)
            print('Error reading JCamp file: ', file)

    def __readRemarks(self, spectrumData):
        """
        Reads the settings which take the format '##SETTING= VALUE'
        Returns 'lineNumber' which is the starting point for reading 
        in the x-y data
        """
        lineNumber = 0
        remarks = {}
        foundXYData = False
        for line in spectrumData:
            remark = re.findall(r'##.+', line) 
            if remark:
                if 'XYDATA=' in remark[0]:
                    foundXYData = True
                    break
                remark = remark[0][2::].split('=')
                remarks[remark[0]] = remark[1]
            lineNumber += 1
        if not foundXYData:
            raise ValueError('XYDATA not found in JCAMP file.')
        return lineNumber+1, remarks
                
    def __get_xy_data(self, spectrumData, lineNumber, cols = 'All'):
        """Reads in the x and y data from a starting point 'lineNumber'"""
        #Check first line for number of columns if cols isn't == 'All'
        if cols == 'All':
            line = spectrumData[lineNumber].split(' ')
            line = [value for value in line if value != '']
            cols = [i for i in range(len(line))]
            
        #A single integer may well have been passed. We need to convert to a list
        elif type(cols) == int:
            cols = [0, cols]
        else:
            cols = [0] + list(cols)
        listOfLists = [[] for i  in cols]
        for line in spectrumData[lineNumber::]:
            if '##END' in line:
                break
            line = line.split(' ')
            line = [value for value in line if value != '']
            i = 0
            for index in cols:
                value = line[index].replace('\n', '')
                listOfLists[i].append(value)
                i += 1
        return listOfLists   

jcamp = JCampReader('jcampTest.jdx')


