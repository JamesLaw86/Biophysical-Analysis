# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 13:06:21 2017

@author: james.law
"""
import sys
if __name__ == '__main__':
    sys.path.append('../')
from Binding import titration_dataset
from Binding import binding
import matplotlib.pyplot as plt


BiMolData = titration_dataset.binding_dataset.setupCSV("Binding Dataset.csv")

results = BiMolData.fitBimolecularSimple(Kd_estimate = 10e-6)
fig = BiMolData.plotFit(results)
