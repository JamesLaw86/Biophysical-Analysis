# -*- coding: utf-8 -*-
"""
Equations to fit binding curves. Equations are taken from:
Pollard, T. D. (2010). A guide to simple and informative binding assays.
Molecular Biology of the Cell, 21(23), 4061–7. https://doi.org/10.1091/mbc.E10-08-0683

"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
#import DataSetHandling.xy_DataSet

def bimolecularSimple(Bfree, Kd):
    """
    Simple bimolecular binding, i.e. A + B <> AB. 
    Assumes [A] is at << lower concentraion than the Kd.
    """
    fracBound = Bfree / (Kd + Bfree)
    return fracBound

def bimolecularHill(Bfree, Kd, n):
    """
    The Hill equation. Simple bimolecular interaction but with cooperativity.
    Again assumes [A] << lower than Kd
    """
    numerator = (Bfree ** n)
    denom = Kd + numerator
    fracBound = numerator / denom
    return fracBound

def bimolecularQuadratic(B_total, A_total, Kd):
    """
    Quadratic binding equation for when [A] is in the same range as the 
    Kd.
    """
    numerator1 = B_total + A_total + Kd
    numerator2 = np.sqrt((B_total + A_total + Kd )** 2 - 4 * B_total * A_total)
    fracBound = (numerator1 - numerator2) / (2 * A_total) 
    return fracBound


def fitExample1(x_axis, y_data, **kwargs):
    """Fit xy_dataset to the equation above."""
    fit = scipy.optimize.curve_fit(bimolecularSimple, x_axis, y_data)
    return fit

#Bfrees = np.linspace(0, 100e-6, 20)
#ABs = bimolecularSimple(Bfrees, 10e-6)
#noise = np.random.normal(ABs, .03)
#plt.plot(ABs)
#plt.plot(noise)
#
#quadTest = bimolecularQuadratic(Bfrees, 10e-8, 10e-6)
#plt.plot(quadTest)
#
#
#fit = fitExample1(Bfrees, noise)
#print(fit)
#
#for n in np.linspace(1, 4, 10):
#    ABs = bimolecularHill(Bfrees, 1e-6, n)
#    #plt.plot(ABs)