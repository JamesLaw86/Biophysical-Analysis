# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 08:26:19 2017

@author: james.law
"""

import binding
import sys
import scipy.optimize
if __name__ == 'main':
    sys.path.append('../')
from DataSetHandling import xy_DataSet
    

class binding_dataset(xy_DataSet.xy_dataSet):
    """
    Class to specifically hold a binding dataset, i.e. concentration
    on the x axis and either concentration of ratio of bound to unbound
    on the y axis
    """
    def fitBimolecularSimple(self, Kd_estimate = 10e-6, **kwargs):
        """
        Fit dataset to the simple bimolecular binding equation.
        kwargs contain arguments to pass to scipy.optimisie.curvefit
        """
        fit = scipy.optimize.curve_fit(binding.bimolecularSimple,
                                       self.x_axis, self.y_data)
        self.addResult('BimolecularSimple', fit)
        