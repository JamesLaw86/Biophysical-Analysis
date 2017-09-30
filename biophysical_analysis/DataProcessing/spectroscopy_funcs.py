# -*- coding: utf-8 -*-
"""
Spectroscopy functions

"""
import numpy as np


""" Functions from the famous Beer Lambert (bl) Law A = ecl"""

def blGetAbs(epsilon, conc, pathLength):
    return epsilon * conc * pathLength

def blGetConc(Abs, epsilon, pathLength):
    return Abs / (epsilon * pathLength)

def blGetEpsilon(Abs, conc, pathLength):
    return Abs / (conc * pathLength)

def TransFromAbs(Abs):
    """
    Transmittence (percentage) from the absorbance value
    A = 2 - log(T)
    A - 2 = -log(T)
    10**-(A-2) = T
    """
    ans = Abs - 2
    ans = 10 ** -ans
    return ans

def AbsorbFromTrans(Trans):
    return (2-np.log10(Trans))

def EstimateEpsilon(seq):
    pass
    
def ApproxConc280(Abs, pathLength = 10):
    """
    Caluclates the approximate protein concentration based on average
    extinction coefficient at 280nm. Can be widely out!!!
    """
    pass

