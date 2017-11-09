# -*- coding: utf-8 -*-
"""
Equations to fit binding curves. Equations are taken from:
Pollard, T. D. (2010). A guide to simple and informative binding assays.
Molecular Biology of the Cell, 21(23), 4061–7. https://doi.org/10.1091/mbc.E10-08-0683

And from https://en.wikipedia.org/wiki/Hill_equation_(biochemistry)

"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize

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
    Kd. Holds true for all A concentrations but requires A_total
    """
    numerator1 = B_total + A_total + Kd
    numerator2 = np.sqrt((numerator1**2) - (4 * B_total * A_total))
    fracBound = (numerator1 - numerator2) / (2 * A_total) 
    return fracBound


def fitExample1(x_axis, y_data, **kwargs):
    """Fit xy_dataset to the equation above."""
    fit = scipy.optimize.curve_fit(bimolecularSimple, x_axis, y_data)
    return fit


def __createTestDataBiSimp(Bstart = 0, Bstop = 100e-6, points = 20, Kd = 10e-6,
                           noise = 0.03):
    with open('Binding Dataset.csv', 'w') as csvFile:
        Bfrees = np.linspace(Bstart, Bstop, points)
        fracBound = bimolecularSimple(Bfrees, Kd)
        noisy_ydata = np.random.normal(fracBound, noise)
        #csvFile.write('Actual Kd,10e-6\n')
        csvFile.write('XUNITS,Concentration (M)\n')
        csvFile.write('YUNITS,Fraction Bound\n')
        csvFile.write('Data\n')
        c = 0
        for i in Bfrees:
            csvFile.write(str(i) + ',' + str(noisy_ydata[c]) + '\n')
            c += 1
            
def __createTestDataHill(Bstart = 1e-12, Bstop = 300e-6, points = 20, 
                         n = 2, Kd = 10e-9, noise = 0.03):
    with open('Hill Dataset.csv', 'w') as csvFile:
            Bfrees = np.linspace(Bstart, Bstop, points)
            fracBound = bimolecularHill(Bfrees, Kd, n)
            noisy_ydata = np.random.normal(fracBound, noise)
            plt.plot(fracBound)
            plt.plot(noisy_ydata)
            #csvFile.write('Actual Kd,10e-6\n')
            #csvFile.write('Actual n,2\n')
            csvFile.write('XUNITS,Concentration (M)\n')
            csvFile.write('YUNITS,Fraction Bound\n')
            csvFile.write('Data\n')
            c = 0
            for i in Bfrees:
                csvFile.write(str(i) + ',' + str(noisy_ydata[c]) + '\n')
                c += 1           

def __createTestDataBiQuad(Bstart = 1e-12, Bstop = 100e-6, Atot = 10e-6,
                           points = 20, Kd = 10e-6, noise = 0.03):
    with open('Binding Dataset Quadratic.csv', 'w') as csvFile:
        Btots = np.linspace(Bstart, Bstop, points)
        frac = bimolecularQuadratic(Btots ,Atot, Kd)
        noisy_ydata = np.random.normal(frac, noise)
        csvFile.write('XUNITS,Concentration (M)\n')
        csvFile.write('YUNITS,Fraction Bound\n')
        #csvFile.write('A_tot,10e-6\n')
        #csvFile.write('Actual Kd,10e-6')
        csvFile.write('Data\n')
        c = 0
        for i in Btots:
            csvFile.write(str(i) + ',' + str(noisy_ydata[c]) + '\n')
            c += 1


if __name__ == '__main__':
    __createTestDataBiSimp()
    __createTestDataHill()
    __createTestDataBiQuad()
