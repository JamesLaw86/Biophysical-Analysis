# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 08:26:19 2017

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
from binding import bindEqs



class Binding_Dataset(xy_DataSet.xy_dataSet):
    """
    Class to specifically hold a binding dataset, i.e. concentration
    on the x axis and either concentration of ratio of bound to unbound
    on the y axis
    """
    
    def fitBimolecularSimple(self, Kd_estimate = 10e-6, plot = False, **kwargs):
        """
        Fit dataset to the simple bimolecular binding equation.
        kwargs contain arguments to pass to scipy.optimisie.curvefit
        """
        popt, pcov = scipy.optimize.curve_fit(bindEqs.bimolecularSimple,
                                           self.x_axis, self.y_data, **kwargs)
        Kd = popt[0]
        y_calc = bindEqs.bimolecularSimple(self.x_axis, Kd)
        residuals = self.y_data - y_calc
        result = {'Kd_fitted' : Kd, 'y_calc' : y_calc, 'residuals': residuals}
        self.addResult('FitBimolecularSimple', result)
        if plot:
            self.plotFit(result)
        return result
    
    
    def fitBimolecularQuadratic(self, Kd_estimate = 10e-6, A_tot = None,
                                plot = False, **kwargs):
        """
        Fit to the quadratic binding equation.
        kwargs contain arguments to pass to scipy.optimisie.curvefit
        """
        #Check if A_tot exists in remarks if not provided
        if not A_tot:
            for remark in self.remarks:
                find = re.findall(r'A_?tot', remark)
                if find[0]:
                    A_tot = float(find[0])
                    print('A_tot read from remarks (', remark, ' with value: ', A_tot)
                    break
        if A_tot < 0 or not A_tot:
            raise ValueError('A_tot is either None or less than zero.\
                             Concentration cannot be negative')
        
        #We want to keep A_tot constant in the fitting, use lamda function as proxy
        func = lambda x_axis, Kd_estimate: bindEqs.bimolecularQuadratic(self.x_axis, 
                                                                        A_tot, Kd_estimate)
        popt, pcov = scipy.optimize.curve_fit(func, self.x_axis, self.y_data,
                                              Kd_estimate)
        Kd = popt[0]
        y_calc = bindEqs.bimolecularQuadratic(self.x_axis, A_tot, Kd)
        residuals = self.y_data - y_calc
        result = {'Kd_fitted' : Kd, 'y_calc' : y_calc, 'residuals': residuals}
        self.addResult('FitBimolecularQuadratic', result)
        if plot:
            self.plotFit(result)
        return result
    
    
    def fitHillEquation(self, Kd_estimate = 10e-6, n_estimate = 1,
                        plot = False, **kwargs):
        """
        Fit y_data to the Hill equation.
        kwargs contain arguments to pass to scipy.optimisie.curvefit
        """
        popt, pcov = scipy.optimize.curve_fit(bindEqs.bimolecularHill,
                                              self.x_axis, self.y_data, 
                                              [Kd_estimate, n_estimate])
        Kd, n = popt
        y_calc = bindEqs.bimolecularHill(self.x_axis, Kd, n_estimate)
        residuals = self.y_data - y_calc
        result = {'Kd_fitted' : Kd, 'n': n, 'y_calc' : y_calc, 'residuals': residuals}
        self.addResult('FitBimolecularHill', result)
        if plot:
            self.plotFit(result)
        return result
        
        
    def plotFit(self, result):
        """
        Plots results of a fit. Returns the figure instance so it can be 
        configured as desired.
        """ 
        fig = plt.figure(figsize=(6, 4))
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
        ax_y_data = plt.subplot(gs[0])
        ax_resid = plt.subplot(gs[1])
        axs = (ax_y_data, ax_resid)
        ax_y_data.plot(self.x_axis, self.y_data, label = 'Original data')
        ax_y_data.plot(self.x_axis, result['y_calc'], label = 'y_calc')
        ax_resid.plot(self.x_axis, result['residuals'], label = 'residuals')
        
        for ax in axs:
            ax.legend()
            ax.set_xlabel(self.x_units)
        fig.tight_layout()
        

if __name__ == '__main__':
    biMolData = Binding_Dataset.setupCSV("Binding Dataset.csv")
    results = biMolData.fitBimolecularSimple(Kd_estimate = 10e-6, plot = True)
    
    quadData = Binding_Dataset.setupCSV('Binding Dataset Quadratic.csv')
    results = quadData.fitBimolecularQuadratic(Kd_estimate = 10e-5,  A_tot =  10e-6,
                                               plot = True)
    
    HillData = Binding_Dataset.setupCSV('Hill Dataset.csv')
    results = HillData.fitHillEquation(Kd_estimate = 10e-9, n_estimate = 2, plot = True)

        