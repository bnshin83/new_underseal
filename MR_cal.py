import numpy as np
import pandas as pd
from scipy.optimize import fsolve
import openpyxl

# Define MR and SN calculation object
######################################################################
class cal_mr_sn(object):
    """
    Calculate the MR-AASHTO value, and structure number
    
    Input:
        d0_9: Read at sensor D0 to D9. Shape:[num_samples,10]
        p: Pressure read. Shape:[num_samples,]. The shape is [num_samples,] instead of [num_samples,1]
        load: the loading read. Shape: [num_samples,]
        d: Depth. It should be a single float number
        
    Output:
        MR value (can be accessed through self.)
        structure number
        Ep value
    """
    def __init__(self,d0_9,p,load,d,a=5.9):
        self.a = a
        self.d = d
        self.d0_9 = d0_9
        self.load = load
        self.p = p
        self.mr = np.zeros(d0_9.shape[0])
        self.ep = np.zeros(d0_9.shape[0])
        self.ae = np.zeros(d0_9.shape[0])
        self.sn = np.zeros(d0_9.shape[0])
        self.sensor_num = np.zeros(d0_9.shape[0])
    
    # Calcualte MR value, store them in self.mr
    def cal_mr(self,idx, sensor_number):
        r = (sensor_number*12)-48
        if self.load[idx] > 9000:
            self.load[idx] = 9000
        self.mr[idx] = 0.24*self.load[idx]/(self.d0_9[idx,sensor_number]*r)
       
    # Calculate Ep by solving the following equation using scipy.optimize.fsolve
    # Store calcualted Ep in self.ep
    def cal_ep(self,idx):       
        def func(x):
            return [1000*1.5*self.p[idx]*self.a*((1/(self.mr[idx]*1000*np.sqrt(1+(self.d/self.a*(x[0]/(self.mr[idx]*1000))**(1./3))**2)))+\
                                          ((1-1/(np.sqrt(1+(self.d/self.a)**2)))/(x[0])))-self.d0_9[idx,0] ]
        initial_guess = 100000
        result = fsolve(func, [initial_guess])[0]
        self.ep[idx] = result
    
    # Calcualte ae value, store calculated ae value in self.ae
    def cal_ae(self,idx):
        self.ae[idx] = np.sqrt(self.a**2+(self.d*(self.ep[idx]/(self.mr[idx]*1000))**(1./3))**2)
    
    # check if it satisfy r>=0.7*ae
    # This function returns a boolean value
    def check_r(self, idx, sensor_number):
        return (sensor_number*12)-48 >= 0.7*self.ae[idx]
    
    # calcualte SN number, store in self.sn
    def cal_sn(self,idx):
        self.sn[idx] = 0.0045*self.d*self.ep[idx]**(1./3)
    
    # The main calculation loop, follows the workflow given in the Excel file
    def main_cal(self):
        for i in range(self.d0_9.shape[0]):
            for sensor_number in [7,8,9]:
                if sensor_number > 9:
                    raise Exception('Exceed the largest sensor number')
                self.cal_mr(i,sensor_number)
                self.cal_ep(i)
                self.cal_ae(i)
                satisfy_check = self.check_r(i, sensor_number)
                if satisfy_check:
                    self.sensor_num[i] = sensor_number
                    break
            self.cal_sn(i)

