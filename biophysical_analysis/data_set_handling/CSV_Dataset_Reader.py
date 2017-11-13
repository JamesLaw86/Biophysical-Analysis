# -*- coding: utf-8 -*-
"""
Class for reading spectra in csv files.
Works fine but really needs refactoring!!

"""

import csv
import re

class csvSpecReader(object):
    """
    Read x-y spectrum / spectra from a csv file.
    
    Constructor takes 'orientation' keyword which refers to whether the 
    x_axis is oriented horizontally or vertically. Change keyword arg 
    to 'Vertical'for x_axis to be vertically orientated.
    
    Constructor takes keyword 'y_Spectra' which should be an list
    or tuple of the columns or rows starting with index 1. That is
    (1,4) will extract the 1st and 4th columns (or rows) of y_data. 
    
    """
    __counter_orientations = {'Vertical': 'Horizontal', 'Horizontal' :'Vertical'}
    
    def __init__(self, file, y_Spectra = 'All', x_orientation = 'Vertical'):
        
        #If y_Spectra is an integer, make this a list. If y_Spectra is 'All' set it to a list containing -1
        if type(y_Spectra) == int:
            y_Spectra = [y_Spectra]
        elif y_Spectra == 'All':
            y_Spectra = [-1]
        try:
            with open(file) as csvFile:
                self.__setup_containers()
                csvReader = csv.reader(csvFile)
                self.__readData(csvReader, y_Spectra, x_orientation)
        #If this fails try reading the alternative orientation
        except ValueError as e:
            print(e)
            error = 'Error reading in CSV file: ' + file + '\n\
            Trying alternitive orientation'
            print(error)
            self.__setup_containers()
            with open(file) as csvFile:
                csvReader = csv.reader(csvFile)
                self.__readData(csvReader, y_Spectra,
                            csvSpecReader.__counter_orientations[x_orientation])
            print('Orientation read in opposite orientation to what was specified')   
    
    def __setup_containers(self):
        """Set/resets the dat containers"""
        self.remarks = {}
        self.xy_data = []
        self.xy_dataDict = {}
        
    def __readData(self, csvReader, y_Spectra, x_orientation):
        """A delegator function"""
        if x_orientation == 'Horizontal':
            self.__readDataH(csvReader, y_Spectra)

        elif x_orientation == 'Vertical':
            self.__readDataV(csvReader, y_Spectra)
        else:
            raise ValueError('x_orientation keyword is neither\
                             "Horizontal" nor "Veritcal"')
        
        #This raises ValueError exception if x_axis is not numeric, a probable orientation mixup
        float(self.xy_data[0][0]) 
        return
        
    def __readDataH(self, csvReader, rows):
        """
        Reads in remarks and data from a csv file in which
        x_axis is in horizontal orientation. 
        
        """
        bFoundData = False
        for row in csvReader:
            if not bFoundData:
                bFoundData = self.__readRemark(row)
                if bFoundData:
                    break
        if not bFoundData:
            raise ValueError('Data start line not found in csv file')
        self.xy_data.append(row[1::])
        if 'XUNITS' in self.remarks:
            x_axis = self.remarks['XUNITS']
        else:
            x_axis = 'x_axis'
        self.xy_dataDict[x_axis] = row[1::]
        dataRowNum = 1   #Row counter, start at 1
        for row in csvReader:
            if rows[0] == -1 or dataRowNum in rows:
                name = row[0]
                data = row[1::]
                if name == '':
                    name = str(dataRowNum)
                self.xy_dataDict[name] = data
                self.xy_data.append(data)
            dataRowNum += 1
        return

    def __readDataV(self, csvReader, columns):
        """
        Reads in remarks and data from a csv file in which
        x_axis is in vertical orientation. 
        
        """
        bFoundData = False
        for row in csvReader:
            if not bFoundData:
                bFoundData = self.__readRemark(row)
                if bFoundData:
                    break
        if not bFoundData:
            raise ValueError('Data start line not found in csv file')
        
        if 'XUNITS' in self.remarks:
            x_units = self.remarks['XUNITS']
        else:
            x_units = 'x_axis'
        
        if columns[0] == -1: #ALL columns! 
            listSize = len(row)
            self.xy_dataDict = {name:[] for name in row[1::]}
            lookUp = {i : row[i] for i in range(listSize)}
        else:
            listSize = len(columns) + 1        
            try:
                self.xy_dataDict = {row[i]:[] for i in columns}
                lookUp = {col : row[col] for col in columns }
            except IndexError:
                print('Warning no column names found, using column nums.')
                self.xy_dataDict = {i:[] for i in columns}
                lookUp = {col : col for col in columns }
        lookUp[0] = x_units
        self.xy_data = [[] for i in range(listSize)]
        self.xy_dataDict[x_units] = []
        
        self.__read_xy_dataV(csvReader, lookUp)
    
    
    def __readRemark(self, row):
        """Reads in remarks until data line is found"""
        bFoundData = False
        if row[0] != '' and 'ata' not in row[0] and 'ATA' not in row:  #ata = D/data'
        #Not yet reached start Point of data
           setting = row[0]
           value = row[1]
           self.remarks[setting] = value
           return bFoundData
        else:
            bFoundData = True
            return bFoundData

    def __read_xy_dataV(self, csvReader, lookUp):
        """Reads in the xy data from the csv file"""
        for row in csvReader:
            j = 0
            for col in sorted(lookUp):
                self.xy_data[j].append(row[col])
                self.xy_dataDict[lookUp[col]].append(row[col])
                j += 1
                
        

#csvTestH = csvSpecReader('HorizontalBare.csv', x_orientation = 'Vertical')

#csvTestV = csvSpecReader('VerticalDataSet.csv','All', x_orientation = 'Horizontal')# 'Vertical')
        
    