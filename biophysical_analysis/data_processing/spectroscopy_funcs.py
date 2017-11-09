# -*- coding: utf-8 -*-
"""
Spectroscopy functions

"""
import numpy as np


""" Functions from the famous Beer Lambert (bl) Law A = ecl"""

def GetAbsBeer(epsilon, conc, pathLength):
    """Returns absorbance from extinction coeff, concentration and pathlength"""
    return epsilon * conc * pathLength

def GetConcBeer(Abs, epsilon, pathLength):
    """Returns concentration from absorbance, extinction coeff, and pathlength"""
    return Abs / (epsilon * pathLength)

def GetEpsilonBeer(Abs, conc, pathLength):
    """Returns extinction coeff from absorbacne, concentration and pathlength"""
    return Abs / (conc * pathLength)

def TransFromAbs(Abs):
    """
    Returns transmittence (percentage) from the absorbance value
    A = 2 - log(T)
    A - 2 = -log(T)
    10**-(A-2) = T
    """
    ans = Abs - 2
    return 10 ** -ans

def AbsFromTrans(Trans):
    """Returns absorbance from a transmittence percentage"""
    return (2-np.log10(Trans))




def EstimateEpsilon(seq):
    pass
    
def ApproxConc280(Abs, pathLength = 10):
    """
    Caluclates the approximate protein concentration based on average
    extinction coefficient at 280nm. Can be widely out!!!
    """
    pass

