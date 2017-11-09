# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 08:13:14 2017

@author: james.law
"""

import sys
import scipy.optimize
import matplotlib.pyplot as plt
from matplotlib import gridspec
import re
if __name__ == '__main__':
    sys.path.append('../')
from data_set_handling import xy_DataSet
from kinetics import equations

class Kinetic_Dataset(xy_DataSet.xy_dataSet):
    """
    Class to specifically hold a kinetic dataset, i.e. time on the x axis 
    and concentration/signal of a species on the y axis
    """
    def fit_first_order(self, Ao = None, k_estimate = 1, plot = False, **kwargs):
        """
        Fit the dataset to the first order rate equation.
        kwargs contain arguments to pass to scipy.optimisie.curvefit.
        Should we fit Ao????
        """
        #if not Ao:
        #    Ao = self.y_data[0]
        popt, pcov = scipy.optimize.curve_fit(equations.first_order,
                                              self.x_axis, self.y_data,
                                              [Ao, k_estimate], **kwargs)
        k_fitted, Ao_fitted = popt[0], popt[1]
        y_calc = equations.first_order(self.x_axis, Ao_fitted, k_fitted)
        residuals = self.y_data - y_calc
        result = {'k_fitted' : k_fitted, 'Ao_fitted' : Ao_fitted,
                  'y_calc' : y_calc, 'residuals': residuals}
        self.addResult('FitFirstOrder', result)
        if plot:
            self.plotFit(result)
        return result

