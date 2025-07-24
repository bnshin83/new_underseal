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

# End of definition
######################################################################

## Please comment out the corresponding print statements if you dont want to see them.

#############################################################################
# Change sheet name to 'SB-WB drop 2' if you want to test the southbound data
#############################################################################
# sheet_name = 'NB-EB Drop 2'
# xls_original = pd.read_excel('FWD Underseal Handcal.xlsm',sheet_name)
# mr_sheet = xls_original[pd.to_numeric(xls_original['Pressure'], errors='coerce').notnull()]

# # Read the cooresponding value in excel file
# load = mr_sheet.iloc[:,2].to_numpy()
# p = mr_sheet.iloc[:,1].to_numpy()
# d0_9 = mr_sheet.iloc[:,3:13].to_numpy()
# egon_mr = mr_sheet.iloc[:,16].to_numpy()
# egon_sn = mr_sheet.iloc[:,17].to_numpy()

# ################### Specify the depth data here ##################
# depth = 20.0
# ################### Specify the depth data here ##################

# # Call "cal_mr_sn" class, make an instance of the class. 
# # Call "main_cal" method inside the class to calculate MR and SN.
# cal_object = cal_mr_sn(d0_9,p=p, load=load,d=depth)
# cal_object.main_cal()

# # SN can be retrived by accessing the variable "sn" inside the "cal_object" instance
# print("Calculated SN numbers are :", cal_object.sn)
# print("Compared with Egon's software, the SN differences are :", cal_object.sn - egon_sn)
# print(" ")

# # MR can be retrived by accessing the variable "mr" inside the "cal_object" instance
# print("Calculated MR numbers are :", cal_object.mr)
# print("Compared with Egon's software, the MR differences are :", cal_object.sn - egon_sn)
# print(" ")

# # You can also check the ep number by accessing "ep" variable inside the "cal_object" instance
# print("Calculated Ep values are :", cal_object.ep)
# print(" ")

# # You can also check the sensor number that is actually being used to calcualte the final value
# # The sensor number should be one of [7,8,9]
# print("Index of the sensor that is actually used to calcualted the final values :",cal_object.sensor_num)
# print(" ")