# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 17:54:13 2017

@author: james.law
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy.constants

def first_order(Ao, k, time, end_signal = 0):
    """
    The first order rate equation (A > B), [A] = [Ao] * (e ^ -kt). Returns change in signal
    as a function of time. Ao = start signal, k = first order rate constant (1/s),
    time is in seconds. end_signal is the residual signal at the end point.
    """
    return (Ao * np.exp(-(k * time))) + end_signal

def first_order_increasing(Afinal, k, time, start_signal = 0):
    """
    First order rate equation (A > B) for when signal increases with time.
    Afinal corresponds to the signal at time = inf. 'start_signal' is
    any signal that exists prior to reaction.
    """
    Afinal += start_signal
    return Afinal - np.exp(-(k * time))

def second_order(Ao, Bo, k, time, end_signal = 0):
    """
    Second order rate equation for when A and B are different reagents.
    Taken from ? Doesn't bloody work!!
    
    [A] = [Ao]([Ao]-[Bo]) / ([Ao]-[Bo]-e ^ -([Ao]-[Bo]) kt
    """
    d_conc = Ao - Bo  #used alot!
    numerator = Ao * d_conc
    denominator = d_conc * np.exp(-(d_conc * k * time))
    return (numerator / denominator)


def second_order_Ao(Ao, k, time):
    """
    Second order rate equation for a single reactant. 
    1/At - 1/Ao = kt => At = 1 / (kt + 1/Ao)
    """
    kt = k * time
    At = 1 / (kt + (1/Ao))
    return At

def michaelis_menten(s, Km, Vmax):
    """
    Standard Michaelis–Menten equation.Returns the initial 
    reation velocity. s = substrate concentration,
    Km = Michaelis–Menten constant and Vmax = maximum velocity
    Assumes [S] >> [E]
    """
    return (Vmax * s) / (Km + s)

def mm_comp_inhib(s, Km, Vmax, alpha):
    pass

def mm_uncomp_inhib(s, Km, Vmax, alpha):
    pass

def eyring(k, T, dS = -10, dH = -100, degC = True):
    """
    The Eyring equation.
    """
    kb = scipy.constants.Boltzmann
    R = scipy.constants.gas_constant
    h = scipy.constants.h
    if degC:
        T = scipy.constants.convert_temperature(T, 'Celcius', 'Kelvin')
    first_mult = (kb * T) / h
    pass

if __name__ == '__main__':
    """Make Examples"""
    time_series = np.linspace(0, 5, 50) #5 seconds!
    first_order_data = first_order(Ao = 0.5, k = 2, time = time_series)
    noisey_data = np.random.normal(first_order_data, 0.025)
    with open('First Order Ex.csv', 'w') as csvFile:
        csvFile.write('XUNITS,Time (s)\n')
        csvFile.write('YUNITS,Abosrbance (AU)\n')
        csvFile.write('Data\n')
        for time, sig in zip(time_series, noisey_data):
            csvFile.write(str(time) + ',' + str(sig) + '\n')
        
    
    
    
