# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 08:26:19 2017

@author: james.law
"""

import sys
import scipy.optimize
import matplotlib.pyplot as plt
if __name__ == '__main__':
    sys.path.append('../')
from DataSetHandling import xy_DataSet
from Binding import binding
    

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
        popt, pcov = scipy.optimize.curve_fit(binding.bimolecularSimple,
                                           self.x_axis, self.y_data, **kwargs)
        Kd = popt[0]
        y_calc = binding.bimolecularSimple(self.x_axis, Kd)
        residuals = self.y_data - y_calc
        results = {'Kd_fitted' : Kd, 'y_calc' : y_calc, 'residuals': residuals}
        self.addResult('FitBimolecularSimple', results)
        return results
    
    def plotFit(self, result):
        """
        Plots results of a fit. Returns the figure instance so it can be 
        configured as desired.
        """ 
        fig = plt.figure()
        ax_y_data = fig.add_subplot(2,1,1)
        ax_resid = fig.add_subplot(2,1,2)
        axs = (ax_y_data, ax_resid)
        ax_y_data.plot(self.x_axis, self.y_data, label = 'Original data')
        ax_y_data.plot(self.x_axis, result['y_calc'], label = 'y_calc')
        ax_resid.plot(self.x_axis, result['residuals'], label = 'residuals')
        
        for ax in axs:
            ax.legend()
            ax.set_xlabel(self.x_units)
        fig.tight_layout()
        


        