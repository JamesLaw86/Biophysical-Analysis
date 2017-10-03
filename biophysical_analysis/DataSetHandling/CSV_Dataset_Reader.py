# -*- coding: utf-8 -*-
"""
Class for reading spectra in csv files.
Works fine but really needs refactoring!!

"""

import csv

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
    def __init__(self, file, y_Spectra = 'All', x_orientation = 'Vertical'):
        with open(file) as csvFile:
            csvReader = csv.reader(csvFile)
            self.remarks = {}
            self.xy_data = []
            self.xy_dataDict = {}
            
            #If y_Spectra is an integer, make this a list
            #If y_Spectra is 'All' set it to a list containing -1
            if type(y_Spectra) == int:
                y_Spectra = [y_Spectra]
            elif y_Spectra == 'All':
                y_Spectra = [-1]
            
            try:
                self.__readData(csvReader, y_Spectra, x_orientation)
            except ValueError as e:
                print(e)
                print('Error reading in CSV file: ', file)
    
    def __readData(self, csvReader, y_Spectra, x_orientation):
        """A delegator function"""
        
        if x_orientation == 'Horizontal':
            self.__readDataH(csvReader, y_Spectra)

        elif x_orientation == 'Vertical':
            self.__readDataV(csvReader, y_Spectra)
        else:
            raise ValueError('x_orientation keyword is neither\
                             "Horizontal" nor "Veritcal"')
        return
        
    def __readDataH(self, csvReader, rows):
        """
        Reads in remarks and data from a csv file in which
        x_axis is in horizontal orientation. 
        
        """
        bFoundData = False
        i = 1
        for row in csvReader:
            if not bFoundData:
                if row[0] != 'Data' and row[0] != '': #Not reached start Point of data
                    setting = row[0]
                    value = row[1]
                    self.remarks[setting] = value
                else:
                    bFoundData = True
                    self.xy_data.append(row[1::])
                    if 'XUNITS' in self.remarks:
                        x_axis = self.remarks['XUNITS']
                    else:
                        x_axis = 'x_axis'
                    self.xy_dataDict[x_axis] = row[1::]
            else:
                if rows[0] == -1 or i in rows:
                    name = row[0]
                    data = row[1::]
                    self.xy_dataDict[name] = data
                    self.xy_data.append(data)
                i += 1
        if not bFoundData:
            raise ValueError('Data start line not found in csv file')
        return

    def __readDataV(self, csvReader, columns):
        """
        Reads in remarks and data from a csv file in which
        x_axis is in vertical orientation. 
        
        """
        bFoundData = False
        for row in csvReader:
            if not bFoundData:
                if row[0] != 'Data' and row[0] != '': #Not yet reached start Point of data
                    setting = row[0]
                    value = row[1]
                    self.remarks[setting] = value
                else:
                    bFoundData = True
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
                        self.xy_dataDict = {row[i]:[] for i in columns}
                        lookUp = {col : row[col] for col in columns }
                    lookUp[0] = x_units
                    self.xy_data = [[] for i in range(listSize)]
                    self.xy_dataDict[x_units] = []
            else:
                #Read in the x-y data!!
                j = 0
                for col in sorted(lookUp):
                    self.xy_data[j].append(row[col])
                    self.xy_dataDict[lookUp[col]].append(row[col])
                    j += 1
        if not bFoundData:
            raise ValueError('Data start line not found in csv file')
        

csvTestH = csvSpecReader('HorizontalDataSet.csv', x_orientation = 'Horizontal')

csvTestV = csvSpecReader('VerticalDataSet.csv','All', x_orientation = 'Vertical')
        
    