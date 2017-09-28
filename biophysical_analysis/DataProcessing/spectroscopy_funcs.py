# -*- coding: utf-8 -*-
"""
Spectroscopy functions

"""

import numpy as np
import data_process

""" Functions from the famous Beer Lambert Law A = ecl"""

def Abs(epsilon, conc, pathLength):
    return epsilon * conc * pathLength

def Conc(Abs, epsilon, pathLength):
    return Abs / (epsilon * pathLength)

def Epsilon(Abs, conc, pathLength):
    return Abs / (conc * epsilon)

#a = log(T)
def Transmittance(Abs):
    T = 10
    return np.log10(Abs)
    
def ApproxConc
