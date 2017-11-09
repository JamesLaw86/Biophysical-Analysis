# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 13:06:21 2017

@author: james.law
"""
import sys
if __name__ == '__main__':
    sys.path.append('../')
from binding.titration_dataset import Binding_Dataset

biMolData = Binding_Dataset.setupCSV("Binding Dataset.csv")
results = biMolData.fitBimolecularSimple(Kd_estimate = 10e-6, plot = True)

quadData = Binding_Dataset.setupCSV('Binding Dataset Quadratic.csv')
results = quadData.fitBimolecularQuadratic(Kd_estimate = 10e-5,  A_tot =  10e-6,
                                           plot = True)

HillData = Binding_Dataset.setupCSV('Hill Dataset.csv')
results = HillData.fitHillEquation(Kd_estimate = 10e-5, n_estimate = 2, plot = True)