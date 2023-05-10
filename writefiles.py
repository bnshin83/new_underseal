from sys import stderr
from webbrowser import get
import numpy as np
import db
import MR_cal as mr
from scipy.stats import hmean
import math
from roadanalyzer import set_vars, calc_esal

def writeLCC(mde, pavtype):
    h = mde["mod_est"][:,3:7][0]
    # print(h)
    # sys.exit(-1)
    thickness = []
    for i in h:
        # print(i)
        if i != 0.0:
            thickness.append(float(i))
    # print(thickness)
    # sys.exit(-1)
    pts = len(mde["mod_est"])
    sensors = 9
    sensor_placement = [abs(float(mde["misc"][0][1])), abs(float(mde["misc"][0][3])), abs(float(mde["misc"][0][5])), abs(float(mde["misc"][0][7])), abs(float(mde["misc"][0][9])), abs(float(mde["misc"][0][11])), abs(float(mde["misc"][0][13])), abs(float(mde["misc"][0][15])), abs(float(mde["misc"][0][17]))]
    sensor_placement_rounded = [round(i) for i in sensor_placement] 
    temp_type = "1"
    pav = None
    if pavtype == "asphalt":
        pav = "0"
    elif pavtype == "concrete":
        pav = "1"
    else:
        pav = "2"
    radius = mde["misc"][0][19]
    prstr = ""
    prstr = str(len(thickness)+1) +"\n"
    for i in thickness:
        prstr = prstr + str(i) + " "
    prstr = prstr + "\n"
    prstr = prstr + "0\n"
    prstr = prstr + str(pts) + "\n"
    prstr = prstr + str(9) + "\n"
    for i in sensor_placement_rounded:
        prstr = prstr + str(i) + " "
    prstr = prstr + "\n"
    prstr = prstr + str(1) + "\n"
    prstr = prstr + str(pav) + "\n"
    prstr = prstr + str(radius)
    # print("***PRINTING prstr******")
    # print(prstr)
    with open("C:/Aashto/LCC.dat", 'w') as f:
        f.write(prstr)
    
    # print("LCC******************************")
    # print(sensor_placement_rounded)
    # print(radius)

def writeLCC0():
    sections = 1
    prstr = str(sections) + " \n"
    with open("C:/Aashto/LCC0.dat", 'w') as f:
        f.write(prstr)

def writeLCC1(testDesc, pavtype, ll_obj):
    esal = calc_esal(ll_obj)
    initservability, termservability, std, iri  = set_vars(testDesc, pavtype)
    prstr = str(esal) + " " + str(initservability) + " " + str(termservability) + " " + str(std)
    with open("C:/Aashto/LCC1.dat", 'w') as f:
        f.write(prstr)

def writeLCC2():
    s = "0.9 0.9 1"
    with open("C:/Aashto/LCC2.dat", 'w') as f:
        f.write(s)


def writeELMOD_FWD(mde, sensordata):
    # chainage = mde["deflections"][:, 1]
    defl = np.array(sensordata[:, 0:9])
    # print("PRINTING DEFL")
    # print(defl)
    points_drops = np.array(mde["deflections_calc"][:, 3:5])
    deflections_all = np.array(mde["deflections"])
    deflections = np.array([tmp for tmp in deflections_all if(list(map(int, tmp[[4,16]])) in points_drops.tolist())])
    chainage = np.array([deflections[:, 1].astype(float)])
    # print(deflections)
    # print("Chainage shape")
    # print(chainage.shape)
    airtemp = np.array([deflections[:, 17].astype(float)])
    surface_temp = np.array([deflections[:, 3].astype(float)])
    pressure = np.array([len(airtemp[0])*[82.06]])
    # print("Pressure shape")
    # print(pressure.shape)
    arr = np.array([])
    arr = np.concatenate((np.transpose(chainage), defl), axis = 1)
    arr = np.concatenate((arr, np.transpose(pressure)), axis = 1)
    arr = np.concatenate((arr, np.transpose(airtemp)), axis = 1)
    arr = np.concatenate((arr, np.transpose(surface_temp)), axis = 1)
    prstr = ""
    for ele in arr:
        for i in ele:
            prstr = prstr + str(i) +" "
        prstr = prstr + "\n"
    # print("****PRINTING ELMOD FWD*****")
    # print(prstr)
    with open("C:/Aashto/ELMOD_fwd.dat", 'w') as f:
        f.write(prstr)



