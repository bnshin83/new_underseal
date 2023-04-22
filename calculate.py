from pdb import line_prefix
from sys import stderr
# from this import d
from webbrowser import get
import numpy as np
import db
import MR_cal as mr
from scipy.stats import hmean
import math
import xlrd
from writefiles import writeELMOD_FWD, writeLCC, writeLCC0, writeLCC1
import subprocess
import sys,os

def temp_correction(temp, thickness):
    temp = 120 if (temp>120) else temp
    temp = 30 if (temp<30) else temp
    thickness = 12 if(thickness > 12) else thickness
    thickness = 2 if(thickness < 2) else thickness

    factor = None

    if(temp>68):
        t12 = -0.011538462*temp + 1.784615385
        t8 = -0.009615385*temp + 1.653846154
        t4 = -0.006346154*temp + 1.431538462
        t2 = -0.003846154*temp + 1.261538462
    else:
        t12 = -0.009539474*temp + 1.648684211
        t8 = -0.008684211*temp + 1.590526316
        t4 = -0.007565789*temp + 1.514473684
        t2 = -0.004276316*temp + 1.290789474

    # print("Thickness: ", thickness)
    # print("Temp: ", temp)
    if(thickness >= 12):
        factor = t12
    elif(thickness >= 8):
        factor = t12 + ((thickness - 12)*(t8 - t12)/(8 - 12))
    elif(thickness >= 4):
        factor = t8 + (thickness - 8)*(t4 - t8)/(4 - 8)
    elif(thickness >= 2):
        factor = t4 + (thickness - 4)*(t2 - t4)/(2 - 4)
    else:
        factor = t2
    return factor
    


def get_E(mde, pavtype, adj_e):

    mod_limits = {"asphalt": 1000, "concrete": 5000, "middle": 150, "subgrade": 80}
    arr = np.array(mde["mod_est"])
    arr = arr[:, [3, 4, 5, 6, 9, 10, 11, 12]]
    arr = arr.astype(float)
    arr = np.transpose(arr)
    # print(arr)


    layers = None
    limits = None
    pavtype = pavtype.lower()
    if (np.all(arr[1:4, :] == 0)):
        layers = 2
        if (pavtype == "asphalt"):
            limits = [mod_limits["asphalt"], mod_limits["subgrade"]]
        elif (pavtype == "concrete"):
            limits = [mod_limits["concrete"], mod_limits["subgrade"]]
    elif (np.all(arr[2:4, :] == 0)):
        layers = 3
        if (pavtype == "asphalt"):
            limits = [mod_limits["asphalt"], mod_limits["middle"], mod_limits["subgrade"]]
        elif (pavtype == "concrete"):
            limits = [mod_limits["concrete"], mod_limits["middle"], mod_limits["subgrade"]]
        elif (pavtype == "composite"):
            limits = [mod_limits["asphalt"], mod_limits["concrete"], mod_limits["subgrade"]]
    elif (np.all(arr[3:4] == 0)):
        layers = 4
        limits = [mod_limits["asphalt"], mod_limits["concrete"], mod_limits["middle"], mod_limits["subgrade"]]
    
    e = arr[4:8, :]
    # print('e:',e)
    # print('e.shape:',e.shape)
    limits_mult = np.array(np.shape(e)[1]*[limits])
    limits_mult = np.transpose(limits_mult)
    # adj_e = 1.319
    # adj_e = float(input("Enter adjusted elmod modulus please: "))
    calc_e = e
    # print(np.shape(limits_mult))
    for i in range(0,limits_mult.shape[0]):
        if(i==0 and (pavtype == "asphalt" or pavtype == "composite")):
            calc_e[0] = e[0,:]/adj_e        
            calc_e[0] = np.round(np.minimum(calc_e[0], limits_mult[0]))
        calc_e[i] = np.round(np.minimum(e[i], limits_mult[i]))
    
    # print("Done with getE")
    # print(np.shape(limits_mult))
    # print(np.shape(e[0:limits_mult.shape[0],:]))
    # calc_e = e[0:limits_mult.shape[0],:]/adj_e
    # print(np.shape(calc_e))
    # calc_e = np.minimum(limits_mult, calc_e)
    # print("Calculated E")
    # print(calc_e)
    # e = np.minimum(e, )

    # con.commit()
    # cursor.close()
    return calc_e

# get_E(db.connect(), 1, "asphalt")


def insitu_cbr(mr):
    mrnp =  np.array(mr)
    insitu = np.minimum(np.full(np.shape(mrnp), 7), mrnp*1000/4500)
    return insitu

def aashto_esals(insitu, ashtoo):
    # sample =  (10^(9.36*(LOG(AB2+1))-0.2+((LOG(0.63))/(0.4+(1094/((AB2+1)^5.19))))+2.32*(LOG(Q2*1000/3))-8.07))
    tmp = np.array(insitu)
    tmp2 = np.array(ashtoo)
    # esals = np.power(10, (9.36*np.log(tmp+1) - 0.2 + ((np.log(0.63))/(0.4+(1094/(np.power(tmp+1, 5.19))))) + 2.32*(np.log(ashtoo*1000/3) -8.07)))
    esals =  np.power(10, (9.36*np.log10(tmp+1) - 0.2 + ((np.log10(0.63))/(0.4+(1094/(np.power(tmp+1, 5.19))))) + 2.32*(np.log10(tmp2*1000/3.0)) - 8.07))
    # print(esals)
    return esals

def indot_esals(surf):

    surfnp = np.array(surf)
    # (5.6*10^10)/(D2^4.6)
    esals = (5.6*(10**10)/(np.power(surfnp, 4.6)))
    return esals

def limit_esals(ashto_esals):
    lim_esal = None
    ###=IF(AC2="","",(IF(AC2>40000000,40000000,AC2)))
    lim_esal = np.array(ashto_esals)
    # print(lim_esal)
    min_lim_esal = np.minimum(np.full(np.shape(lim_esal), 40000000), lim_esal)
    return min_lim_esal

def insitu_mr(mr_ashto):
    mr = np.array(mr_ashto)
    mr = np.minimum(np.full(np.shape(mr) , 31500), mr*1000/3)
    return mr

def get_log(sgd):
    log = np.array(sgd)
    log = np.log10(log)
    return log

def getSurfaceDefCrit(mde):
    road = mde["misc"][0][-1]
    # print(road)
    defcrit = None
    if (road == 'i'):
        defcrit = 8
    elif (road == 'u'):
        defcrit = 10
    elif (road == 's'):
        defcrit = 12
    return defcrit

# def getSgdCrit(sgd):
#     logsgd = np.log10(sgd)


#For NB-EB/SB-WB ESALS sheet
def getESALS_reliability(hmeans, pavtype):
    sn = hmeans["sn"]
    remesals = hmeans["remesals"]
    mod_res = hmeans["mod_res"]
    iri = None
    if(pavtype == "asphalt"):
        iri = 120
    elif(pavtype == "concrete"):
        iri = 140
    elif(pavtype == "composite"):
        iri = 130
    
    iri_metric = iri * 0.015875
    # print("irimetric: ", iri_metric)
    iri_metric = round(iri_metric, 2)
    # iri_metric = 2.22
    # print("irimetric: ", iri_metric)
    estimated_psi = 5 + 0.6046*(np.log10(1+(2.2704*(iri_metric**2)))**3) - 2.2217*(np.log10(1+(2.2704*(iri_metric**2))))**2 - 0.0434*(np.log10(1+(2.2704*(iri_metric**2))))
    # estimated_psi = 5 + 0.6046*(np.log(1+(2.704*(iri_metric**2)))**3) - 2.2217*(np.log(1+(2.2704*(iri_metric**2))))**2 - 0.0434*(np.log(1+(2.2704*(iri_metric**2))))
    estimated_psi = round(min(4.2, estimated_psi), 2)
    # estimated_psi = 3.1
    baseline_esals = 10**(9.36*np.log10(sn+1) - 0.2 + np.log10((estimated_psi - 2.5)/(4.2-1.5))/(0.4+1094/((sn+1)**5.19)) + 2.32*np.log10(mod_res) -8.07)
    # baseline_esals = 10**(np.log10((estimated_psi - 2.5)/(4.2-1.5))/(0.4+1094/((sn+1)**5.19)))
    # baseline_esals = 10**(9.36*math.log10(sn+1) - 0.2)
    baseline_esals = min(40000000, baseline_esals)
    so_coeff = 0.35
    esal_95percent = 10**((-1.645*so_coeff) + 9.36*np.log10(sn+1) - 0.2 + np.log10((estimated_psi - 2.5)/(4.2-1.5))/(0.4+1094/(sn+1)**5.19) + 2.32*np.log10(mod_res) - 8.07)
    esal_95percent = min(40000000, esal_95percent)

    esal_90percent = 10**((-1.282*so_coeff) + 9.36*np.log10(sn+1) - 0.2 + np.log10((estimated_psi - 2.5)/(4.2-1.5))/(0.4+1094/((sn+1)**5.19)) + 2.32*np.log10(mod_res) - 8.07)
    esal_90percent = min(40000000, esal_90percent)

    esal_80percent = 10**((-0.841*so_coeff) + 9.36*np.log10(sn+1) - 0.2 + np.log10((estimated_psi - 2.5)/(4.2-1.5))/(0.4+1094/((sn+1)**5.19)) + 2.32*np.log10(mod_res) - 8.07)
    esal_80percent = min(40000000, esal_80percent)

    # print("Stats NB-EB esals")
    # print("estimated psi: ", estimated_psi)
    # print("baseline esal: ", baseline_esals)
    # print("esal 95: ", esal_95percent)
    # print("esal 90", esal_90percent)
    # print("esal 80", esal_80percent)
    ans = {"iri": iri, "iri_metric": iri_metric,"hmeans": hmeans, "estimated psi": estimated_psi, "baseline esals": baseline_esals, "esal 95": esal_95percent, "esal 90": esal_90percent, "esal 80": esal_80percent}
    return ans
    # IF(10^((-1.645*$I$12)+9.36*LOG10($I$3+1)-0.2+LOG10((I9-2.5)/(4.2-1.5))/(0.4+1094/($I$3+1)^5.19)+2.32*LOG10($I$5)-8.07)>40000000,40000000,10^((-1.645*$I$12)+9.36*LOG10($I$3+1)-0.2+LOG10((I9-2.5)/(4.2-1.5))/(0.4+1094/($I$3+1)^5.19)+2.32*LOG10($I$5)-8.07))
    # IF(10^((-1.282*$I$12)+9.36*LOG10($I$3+1)-0.2+LOG10((I9-2.5)/(4.2-1.5))/(0.4+1094/($I$3+1)^5.19)+2.32*LOG10($I$5)-8.07)>40000000,40000000,10^((-1.282*$I$12)+9.36*LOG10($I$3+1)-0.2+LOG10((I9-2.5)/(4.2-1.5))/(0.4+1094/($I$3+1)^5.19)+2.32*LOG10($I$5)-8.07))

    # IF(10^(9.36*LOG10($I$3+1)-0.2+LOG10(($I$9-2.5)/(4.2-1.5))/(0.4+1094/($I$3+1)^5.19)+2.32*LOG10($I$5)-8.07)>40000000,40000000,10^(9.36*LOG10($I$3+1)-0.2+LOG10(($I$9-2.5)/(4.2-1.5))/(0.4+1094/($I$3+1)^5.19)+2.32*LOG10($I$5)-8.07))
    #  IF((5+0.6046*(LOG(1+(2.2704*($I$8^2))))^3    -2.2217*(LOG(1+(2.2704*($I$8^2))))^2     -0.0434*(LOG(1+(2.2704*($I$8^2)))))>4.2,4.2,5+0.6046*(LOG(1+(2.2704*($I$8^2))))^3-2.2217*(LOG(1+(2.2704*($I$8^2))))^2-0.0434*(LOG(1+(2.2704*($I$8^2)))))

# getESALS_reliability({"sn": 3.74, "remesals": 1183747, "mod_res": 5834}, "asphalt")


def getstats(arr):
    mean = np.mean(arr, axis = 0)
    stddev = np.std(arr, axis = 0)
    max = np.max(arr, axis = 0)
    min = np.min(arr, axis = 0)
    harmean = hmean(arr, axis = 0)
    return [mean, stddev, max, min, harmean]

def putdata(con, data, id):
    sensordata = data["sensordata"]
    # print(sensordata)
    idarr = np.array([sensordata.shape[0]*[id]])
    # print("*********ID***********")
    # print(idarr)
    # print("Points again2: ")
    # print(data["point"])
    tmparr = np.concatenate((np.transpose(idarr), np.transpose([data["point"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["drop_no"]])), axis = 1)
    tmparr = np.concatenate((tmparr, sensordata), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["load"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["pressure"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["sn"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["mr"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["cbrarr"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["aash_esals"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["ind_esals"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["lim_esals"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["insitumr"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["logsgd"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose([data["logmr"]])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose(data["e"])), axis = 1)
    
    # tmparr = np.transpose(tmparr)
    # print(tmparr.shape)
    arr = list(map(tuple, tmparr))
    # print(arr)
    cursor = con.cursor()
    # print(arr)
    cursor.executemany("INSERT INTO CALC VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28)", arr)
    con.commit()
    cursor.close()       
    # sensordata = sensordata.tolist()
    # cursor = con.cursor()
    # cursor.executemany("INSERT IN CALC ")

def putstats(con, data, id):
    arr = []

    # print("*********Printing sensorstats***********")
    # print((np.transpose(data["sensorstats"])))
    # print(len(data["sensorstats"]))
    # print("********************")
    # arr.append([id, "sensorstats"]+data["sensorstats"].tolist())
    sensorstats = np.transpose(data["sensorstats"])
    # print(data["mr_stats"])
    for i in range(0, 10):
        label = "D"+str(i)
        # print(sensorstats[i])
        arr.append([id, label] + list(sensorstats[i]))


    arr.append([id, "mr"]+data["mr_stats"])
    arr.append([id, "sn"]+data["sn_stats"])
    arr.append([id, "cbr"]+data["cbr_stats"])
    arr.append([id, "aash_esals"]+data["aash_esals"])
    arr.append([id, "ind_esals"]+data["ind_esals"])
    arr.append([id, "lim_esals"]+data["lim_esal"])
    arr.append([id, "insitumr"]+data["insitumr"])
    # arr = np.transpose(arr)
    # print(np.shape(arr))
    arr = list(map(tuple, arr))
    # print(arr)
    cursor = con.cursor()
    cursor.executemany("INSERT INTO STATS VALUES (:1, :2, :3, :4, :5, :6)", arr)
    con.commit()
    cursor.close()


def get_data(mde, pavtype, roadtype, row):

    points_drops = np.array(mde["deflections_calc"][:, 3:5])
    deflections_all = np.array(mde["deflections"])
    # print('Shape of deflections_all: {}'.format(deflections_all.shape))
    deflections = np.array([tmp for tmp in deflections_all if(list(map(int, tmp[[4,16]])) in points_drops.tolist())])
    # print("DEFLECTIONS in get_data")
    # print(deflections)
    sensordata = deflections[:, 7:16].astype(float)
    point = np.array(mde["deflections_calc"][:, 4])
    drop_no = np.array(mde["deflections_calc"][:, 3])
    load = np.array([9004.432] * point.shape[0])
    pressure = deflections[:, 5].astype(float)
    temp = deflections[:, 3].astype(float)
    pressure_corr = 82.06/pressure
    pressure_corr = np.reshape(pressure_corr, (pressure_corr.shape[0], 1))
    sensordata = pressure_corr * sensordata

    mod_est = np.array(mde["mod_est"])
    h1 = mod_est[:, 3].astype(float)
    h2 = mod_est[:, 4].astype(float)
    h3 = mod_est[:, 5].astype(float)
    h4 = mod_est[:, 6].astype(float)
    thickness = h1[0] + h2[0] + h3[0] + h4[0]
    temp = np.mean(temp)
    tempcorr, adj_elm, pcc_mod, rxn_subg = writeAndExecute(mde, pavtype, roadtype, row, sensordata)
    # print("TEMP Corr: ", tempcorr)
    # print("Adj Elm: ", adj_elm)
    # tempcorr = temp_correction(temp, thickness)
    # if(pavtype == "asphalt"):
    tmp = tempcorr*sensordata[:, 0]
    # else:
    #     tmp = sensordata[:, 0]
    sensordata = np.insert(sensordata, 0, tmp, axis = 1)
    sensordata = np.round(sensordata, decimals = 2)
    load = np.reshape(load, (load.shape[0],))
    pressure = np.reshape(pressure, (pressure.shape[0],))
    pressure_for_calc = np.array(pressure.shape[0]*[82.06])
    pressure_for_calc = np.reshape(pressure_for_calc, (pressure.shape[0],))
    
    # print("Shapes: ")
    # print("Sensordata: ", sensordata.shape)
    # print("deflections: ", deflections.shape)
    # print("deflections_all: ", deflections_all.shape)
    # print("pressure: ", pressure_for_calc.shape)
    # print("load: ", load.shape)
    # print("thickness: ", thickness.shape)

    
    cal_obj = mr.cal_mr_sn(sensordata,pressure_for_calc, load, thickness)
    cal_obj.main_cal()
    return deflections, sensordata, pressure, load, cal_obj, point, drop_no, adj_elm, pcc_mod, rxn_subg


def getInvalidSections(mde, calc_data, d0crit, subgdcrit, pavtype):
    # print("IS this where it crashed")
    sensordata = calc_data["sensordata"]
    invalid_table = []
    new_stats = {"e1": [], "e2": [], "sn": [], "mr": [], "cbr": [], "k": []}
    for i in range(sensordata.shape[0]):
        # if(sensordata[i][0] > d0crit or sensordata[i][0] < subgdcrit):
        if(sensordata[i][0] > d0crit):
            # print("Reached here2")
            drop_no = calc_data["drop_no"][i]
            point = calc_data["point"][i]
            # print("Reached here3")
            if(pavtype == "concrete"):
                e1 = 0
                e2 = calc_data["e"][0][i]
            elif(pavtype == "asphalt"):
                e2 = 0
                e1 = calc_data["e"][0][i]
            else:
                e1 = calc_data["e"][0][i]
                e2 = calc_data["e"][1][i]
            # print("Reached here")
            chainage = None
            chainage2 = None
            for j in range(np.shape(mde["deflections"])[0]):
                # print(mde["deflections"][j][4])
                # print(mde["deflections"][j][16])
                # print(drop_no)
                # print(point)
                # print()
                if(int(mde["deflections"][j][4]) == int(drop_no) and int(mde["deflections"][j][16]) == int(point)):
                    # print("Matched!!!")
                    chainage = mde["deflections"][j][1]
                    if((j+2) < np.shape(mde["deflections"])[0]):
                        # print("Entered if")
                        chainage2 = mde["deflections"][j+2][1]
                    else:
                        chainage2 = chainage + 320
                    break
            # print("Appending")
            # print(chainage)
            # print(chainage2)
            invalid_table.append([round(float(chainage)*3.281), round(float(chainage2)*3.281)-1, abs((round(float(chainage2)*3.281)-1-round(float(chainage)*3.281))), e1, e2])
            # print(invalid_table)
            # np.append(invalid_table, np.array([chainage, chainage2, chainage2-chainage, e1, e2]))
            # print(sensordata[i][0], " ", subgdcrit, " ", d0crit)
            # print(i, "th entry is out of bounds, please check\n")
        else:
            if(pavtype == "concrete"):
                new_stats["e1"].append(0)
                new_stats["e2"].append(calc_data["e"][0][i])
            elif(pavtype == "asphalt"):
                new_stats["e2"].append(0)
                new_stats["e1"].append(calc_data["e"][0][i])
            else: # type is composite
                new_stats["e2"].append(calc_data["e"][1][i]) # Concrete
                new_stats["e1"].append(calc_data["e"][0][i]) # Asphalt
            
            new_stats["sn"].append(calc_data["sn"][i])
            # print("Printing for dbg...")
            # print(calc_data["insitumr"])
            new_stats["mr"].append(calc_data["insitumr"][i])
            new_stats["cbr"].append(calc_data["cbrarr"][i])
            # print(np.shape(calc_data["pcc_mod"]))
            new_stats["k"].append(calc_data["pcc_mod"][i])
    # print("Return?")
    # print("INVALID TABLE")
    # print(invalid_table)
    return invalid_table, new_stats



# try:


#     except Exception as e:
#         print("Error in running YGJ exe. Please check")
#         print(e)
#         delete_rows(con, "LONGLIST", id)
#         sys.exit(-1)

def blockPrint():
    sys.stdout = open(os.devnull, 'w')
def enablePrint():
    sys.stdout = sys.__stdout__

def writeAndExecute(mde, pavtype, roadtype, row, sensordata):
   # Block the print during execution of Egon's code
    # blockPrint()
    writeLCC(mde, pavtype)
    writeLCC0()
    writeLCC1(roadtype, pavtype, row)
    writeELMOD_FWD(mde, sensordata)
    subprocess.call("C:/Aashto/YGJ.exe")
    # Restore the print after execution of Egon's code
    # enablePrint()
    temp_corr = None
    adj_elm = None
    with open("C:/Aashto/RESULT.dat") as f:
        line = f.readline()
        line = f.readline()
        adj_elm = float(line.split()[-1])
        line = f.readline()
        temp_corr = float(line.split()[1])
        # print(temp_corr)
        # print(adj_elm)
    
    with open("C:/Aashto/K_value.dat") as f:
        line = f.readline()
        # print(line)
        pcc_mod = []
        rxn_subg = []
        line = f.readline()
        # print(line)
        while(len(line.split()) != 0):
            pcc_mod.append(float(line.split()[1]))
            # print(float(line.split()[1]))
            rxn_subg.append(float(line.split()[2]))
            line = f.readline()
            # print(line)
    
    # print("PCC MOD incoming")
    # print(pcc_mod)
    return temp_corr, adj_elm, pcc_mod, rxn_subg
        

def calc(con, id, pavtype, roadtype, row, mde):
    deflections, sensordata, pressure, load, cal_obj, point, drop_no, adj_elm, pcc_mod, rxn_subg = get_data(mde, pavtype, roadtype, row)
    # deflections, sensordata, pressure, load, cal_obj, point, drop_no = get_data(con, id)
    # print("Points again")
    # print(point)
    sn = cal_obj.sn
    mr = cal_obj.mr
    cbrarr = insitu_cbr(mr)
    aash_esals = aashto_esals(sn, mr)
    ind_esals = indot_esals(sensordata[:,0])
    lim_esals = limit_esals(aash_esals)
    insitumr = insitu_mr(mr)
    logsgd = get_log(sensordata[:,8])
    logmr = get_log(mr)

    #####cbr how to get? what is CoV?
    cbr = 3
    mr_again = 3 * 4.5
    logmr_again = np.log10(mr_again)
    reg_line = np.polyfit(logmr, logsgd, 1)
    # print(reg_line)
    # print("logmr_again: ", str(logmr_again))
    subgd_calc = 10**(logmr_again*reg_line[0]+reg_line[1])
    e = get_E(mde, pavtype, adj_elm)

    sensor_stats = getstats(sensordata)
    mr_stats = getstats(mr)
    sn_stats = getstats(sn)
    cbr_stats = getstats(cbrarr)
    aash_esals_stats = getstats(aash_esals)
    ind_esals_stats = getstats(ind_esals)
    lim_esals_stats = getstats(lim_esals)
    insitu_mr_stats = getstats(insitumr)
    # print("Roadtype: ", getSurfaceDefCrit(mde))
    d0crit = getSurfaceDefCrit(mde)
    # print("D0 Crit is done here")
    # getInvalidSections(mde, sensordata, d0crit, subgd_calc)
    # print("Invalid sections dealt with here")
    hmeans = {"sn": sn_stats[4], "remesals": lim_esals_stats[4], "mod_res": insitu_mr_stats[4]}
    esals_sheet = getESALS_reliability(hmeans, pavtype)
    misc = mde["misc"][0]
    # print(misc)
    misc = np.append(misc, esals_sheet["estimated psi"])
    misc = np.append(misc, esals_sheet["baseline esals"])
    misc = np.append(misc, esals_sheet["esal 95"])
    misc = np.append(misc, esals_sheet["esal 90"])
    misc = np.append(misc, esals_sheet["esal 80"])
    mde["misc"] = [misc]
    # print(misc)
    # print("MDE misc inside func: ")
    # print(mde["misc"][0])
    # print()
    calc_data = {"e": e, "drop_no": drop_no, "point": point, "sensordata": sensordata, "mr": mr, "sn": sn, "aash_esals": aash_esals, "ind_esals": ind_esals, "lim_esals": lim_esals, "insitumr": insitumr, "logsgd": logsgd, "logmr": logmr, "cbrarr": cbrarr, "pressure": pressure, "load": load, "pcc_mod": pcc_mod, "rxn_subg": rxn_subg, "esals_sheet": esals_sheet}
    # putdata(con, calc_data, id)
    stats_data = {"sensorstats": sensor_stats, "mr_stats": mr_stats, "sn_stats": sn_stats, "cbr_stats": cbr_stats, "aash_esals": aash_esals_stats, "ind_esals": ind_esals_stats, "lim_esal": lim_esals_stats, "insitumr": insitu_mr_stats, "subgd_calc": subgd_calc, "d0crit": d0crit}
    # putstats(con, stats_data, id)
    invalid_table = []
    new_stats = []
    if(pavtype!="asphalt"):
        invalid_table, new_stats = getInvalidSections(mde, calc_data, d0crit, subgd_calc, pavtype)
    calc_data["invalid_table"] = invalid_table
    calc_data["new_stats"] = new_stats
    return calc_data, stats_data, mde, pcc_mod, rxn_subg







# get_data(db.connect(), 1)
# getSurfaceDefCrit(db.connect(), 1)
# calc(db.connect(), 2, "asphalt")
