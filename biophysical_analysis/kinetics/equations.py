# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 17:54:13 2017

@author: james.law
"""
import numpy as np
import matplotlib.pyplot as plt

def first_order(Ao, k, time):
    """
    The first order rate equation (A > B), [A] = [Ao] * (e ^ -kt). Returns change in signal
    as a function of time. Ao = start signal, k = first order rate constant (1/s),
    time is in seconds.
    """
    return Ao * np.exp(-(k * time))

def first_order_increasing(Afinal, k, time, start_signal = 0):
    """
    First order rate equation (A > B) for when signal increases with time.
    Afinal corresponds to the signal at time = inf. 'start_signal' is
    any signal that exists prior to reaction.
    """
    Afinal += start_signal
    return Afinal - np.exp(-(k * time))

def second_order(Ao, Bo, k, time):
    """
    1 / ([Bo] - [Ao])
    """
    pass

def second_order_Ao(Ao, k, time):
    """
    Second order rate equation for a single reactant. 
    1/At - 1/Ao = kt => At = 1 / (kt + 1/Ao)
    """
    kt = k * time
    At = 1 / (kt + (1/Ao))
    return At

time_series = np.linspace(0, 10)

a  = first_order(1, 1, time_series)

b = first_order_increasing(1, 1, time_series)

d = second_order_Ao(1, 1, time_series)

plt.plot(a)
plt.plot(b)
plt.plot(d)
