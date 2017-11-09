# -*- coding: utf-8 -*-
"""
Free standing commonly used functions for data processing in BioPhysics. 
These generally accept one or more lists of data. We usually work with
2 dimensional datasets, i.e. have an x_axis (dependient variable) and a 
y_axis (Independent variable).  

"""

import numpy as np
import scipy.signal
        
#Test Data. A Circular Dichroism Spectrum form the PCDDB
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    with open('Rhomboid protease glpG.csv') as csvFile:
        data = csvFile.readlines()
        xdim_test = data[1].split(',')
        y_test = np.array(data[0].split(','), dtype = float)
        y_testMultiple = [y_test * i for i in range(1, 11)]
        

def makeArrays(y_data, dtype = None):
    """Creates numpy arrays from lists of spectra/y_data"""
    if dtype:
        arrays = [np.array(dataArray, dtype = dtype) for dataArray in y_data]
    else:
        arrays = [np.array(dataArray) for dataArray in y_data]
    return arrays


def normaliseArea(y_data, area = 1):
    """
    Normalises to the absolute area under the curve. I.e. makes all
       values postive and divides by their total sum.
    """
    spectrum = np.array(y_data, dtype = float)
    if spectrum.ndim > 1:
        raise ValueError('Recieved multidimensional spectrum, \
                          normaliseArea does not support this')
    summed = np.sum(np.abs(spectrum))
    return spectrum/summed


def setDataRange(y_data, x_axis, x_high, x_low):
    """
    Truncates a spectrum and it's x-axis dimension into a smaller spectrum.
    Can truncate multple spectra passed as a list.
    """
    y_data, x_axis = makeArrays([y_data, x_axis], dtype = float)
    if x_axis.ndim > 1 or y_data.ndim > 2:
        raise ValueError('setDataRange was passsed a multidimensional\
                         x_axis\ or spectrum that cannot be processed')
    lowInd = np.abs(x_axis - x_low).argmin()
    highInd = np.abs(x_axis - x_high).argmin()
    if lowInd > highInd:
        temp = highInd
        highInd = lowInd
        lowInd = temp
    highInd += 1
    x_axis = x_axis[lowInd:highInd]
    if y_data.ndim == 1:
        y_data = y_data[lowInd:highInd]
    else:
        y_data = [indv[lowInd:highInd] for indv in y_data]
    y_data = np.array(y_data)
    return y_data, x_axis


def thinData(y_data, x_axis, reductionFactor = 2, startIndex = 0):
    """
    Reduces the number of data points by a factor of "reductionFactor"
    This is useful when we are working with datasets with different steps.
    StartIndex defines where we start the thinning.
    """
    y_data, x_axis = makeArrays([y_data, x_axis])
    if x_axis.ndim > 1 or y_data.ndim > 2:
        raise ValueError('thin data was passsed a multidimensional x_axis\
                          or spectrum. Cannot be processed')
    x_axis = [x for x in x_axis[startIndex::reductionFactor]]
    if y_data.ndim == 1:
        y_data = [datum for datum in y_data[startIndex::reductionFactor]]
    else:
        y_data = [indv[startIndex::reductionFactor] for indv in y_data]
    y_data = np.array(y_data)
    return y_data, x_axis


def baryCentricMean(y_data, x_axis):
    """Caluculates the "centre of intensity" (simlar to centre of mass 
       of a spectrum with respect to the x_axis"""
    y_data, x_axis = makeArrays([y_data, x_axis], dtype = float)
    num = np.sum(y_data * x_axis)
    den = np.sum(y_data)
    bcm = num/den
    return bcm
       
def smooth(y_data, window = 7, polyorder= 3):
    """
    Just uses the savitsy golay algorithm in scipy.signal!
    """
    return scipy.signal.savgol_filter(y_data, window, polyorder)

    
def firstDerivative(y_data, x_axis, window = 7, polyorder= 3):
    """
    Just uses the savitsy golay algorithm in scipy.signal!
    """
    return scipy.signal.savgol_filter(y_data, window, polyorder, deriv = 1)
    
def secondDerivative(y_data, window = 7, polyorder= 3):
    """
    Just uses the savitsy golay algorithm in scipy.signal!
    """
    return scipy.signal.savgol_filter(y_data, window, polyorder, deriv = 2)


def Ratio(y_data):
    """Calculates the ratio of potive to negative values of a spectrum
        Returns a single value"""
    if not y_data[y_data < 0]:
        raise ValueError('All data is posive, ratio cannot be calculated')
    y_data = np.array(y_data, dtype = float)
    pos = np.sum(y_data[y_data > 0])
    neg = np.sum(y_data[y_data < 0])
    return pos/neg


def blend(spec1, spec2, n = 18):
    """
    Performs a linear combination of two spectra such that we go from
    100% of spec1 (0% spec2), to 100% spec2 (0% spec1) in 'n' steps. 
    Returns a dictionary of spectra with keys being the fraction of
    spec2. Will return n+2 spectra, i.e. includes spec1 and spec2!
    """
    spec1, spec2 = makeArrays([spec1, spec2], dtype = float)
    blended = {0 : spec1, 1 : spec2}
    increment = 1 / (n + 1)
    frac2 = 0
    for i in range(n + 1):
        frac1 = 1 - frac2
        component1 = spec1 * frac1
        component2 = spec2 * frac2
        resultant = component1 + component2
        blended[frac1] = resultant
        frac2 += increment
    return blended


