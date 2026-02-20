import numpy as np
import db
import MR_cal as mr
from scipy.stats import hmean
import math
import xlrd
from writefiles import writeELMOD_FWD, writeLCC, writeLCC0, writeLCC1
import subprocess

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
    


def get_E(mde, pavtype, adj_e, special_case):

    mod_limits = {"asphalt": 1000, "concrete": 5000, "middle": 150, "subgrade": 80}
    arr = np.array(mde["mod_est"])
    arr = arr[:, [3, 4, 5, 6, 9, 10, 11, 12, 13]]
    arr = arr.astype(float)
    arr = np.transpose(arr)
    if special_case:
        return arr[4:9, :]

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
    
    e = arr[4:9, :]
    limits_mult = np.array(np.shape(e)[1]*[limits])
    limits_mult = np.transpose(limits_mult)
    calc_e = e
    for i in range(0,limits_mult.shape[0]):
        if(i==0 and (pavtype == "asphalt" or pavtype == "composite")):
            calc_e[0] = e[0,:]/adj_e        
            calc_e[0] = np.round(np.minimum(calc_e[0], limits_mult[0]))
        calc_e[i] = np.round(np.minimum(e[i], limits_mult[i]))
    
    return calc_e


def insitu_cbr(mr):
    mrnp =  np.array(mr)
    insitu = np.minimum(np.full(np.shape(mrnp), 7), mrnp*1000/4500)
    return insitu

def aashto_esals(insitu, ashtoo):
    # sample =  (10^(9.36*(LOG(AB2+1))-0.2+((LOG(0.63))/(0.4+(1094/((AB2+1)^5.19))))+2.32*(LOG(Q2*1000/3))-8.07))
    tmp = np.array(insitu)
    tmp2 = np.array(ashtoo)
    # esals = np.power(10, (9.36*np.log(tmp+1) - 0.2 + ((np.log(0.63))/(0.4+(1094/(np.power(tmp+1, 5.19))))) + 2.32*(np.log(ashtoo*1000/3) -8.07)))
    # =IF(AB2="","",(10^(9.36*(LOG(AB2+1))
    #                    -0.2
    #                    +((LOG(0.63))/(0.4+(1094/((AB2+1)^5.19))))
    #                +2.32*(LOG(Q2*1000/3))-8.07)))

    # (10^(9.36*(LOG(AB2+1))
    #      -0.2
    #      +((LOG(0.63))/(0.4+(1094/((AB2+1)^5.19))))+2.32*(LOG(Q2*1000/3))-8.07))

    esals =  np.power(10, (9.36*np.log10(tmp+1) - 0.2 + ((np.log10(0.63))/(0.4+(1094/(np.power(tmp+1, 5.19))))) + 2.32*(np.log10(tmp2*1000/3.0)) - 8.07))
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
    if (road == 'i'):
        defcrit = 8
    elif (road == 'u'):
        defcrit = 10
    # If the route name is not specified or it is SR, follow the highest DefCrit
    else:
        defcrit = 12
    return defcrit


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
    iri_metric = round(iri_metric, 2)
    estimated_psi = 5 + 0.6046*(np.log10(1+(2.2704*(iri_metric**2)))**3) - 2.2217*(np.log10(1+(2.2704*(iri_metric**2))))**2 - 0.0434*(np.log10(1+(2.2704*(iri_metric**2))))
    estimated_psi = round(min(4.2, estimated_psi), 2)
    baseline_esals = 10**(9.36*np.log10(sn+1) - 0.2 + np.log10((estimated_psi - 2.5)/(4.2-1.5))/(0.4+1094/((sn+1)**5.19)) + 2.32*np.log10(mod_res) -8.07)
    baseline_esals = min(40000000, baseline_esals)
    so_coeff = 0.35
    esal_95percent = 10**((-1.645*so_coeff) + 9.36*np.log10(sn+1) - 0.2 + np.log10((estimated_psi - 2.5)/(4.2-1.5))/(0.4+1094/(sn+1)**5.19) + 2.32*np.log10(mod_res) - 8.07)
    esal_95percent = min(40000000, esal_95percent)

    esal_90percent = 10**((-1.282*so_coeff) + 9.36*np.log10(sn+1) - 0.2 + np.log10((estimated_psi - 2.5)/(4.2-1.5))/(0.4+1094/((sn+1)**5.19)) + 2.32*np.log10(mod_res) - 8.07)
    esal_90percent = min(40000000, esal_90percent)

    esal_80percent = 10**((-0.841*so_coeff) + 9.36*np.log10(sn+1) - 0.2 + np.log10((estimated_psi - 2.5)/(4.2-1.5))/(0.4+1094/((sn+1)**5.19)) + 2.32*np.log10(mod_res) - 8.07)
    esal_80percent = min(40000000, esal_80percent)

    ans = {"iri": iri, "iri_metric": iri_metric,"hmeans": hmeans, "estimated psi": estimated_psi, "baseline esals": baseline_esals, "esal 95": esal_95percent, "esal 90": esal_90percent, "esal 80": esal_80percent}
    return ans


def getstats(arr):
    mean = np.mean(arr, axis = 0)
    stddev = np.std(arr, axis = 0)
    max = np.max(arr, axis = 0)
    min = np.min(arr, axis = 0)
    harmean = hmean(arr, axis = 0)
    return [mean, stddev, max, min, harmean]

def get_data(mde, pavtype, roadtype, ll_obj):
    #           0         1                2       3       4      5      6      7      8      9     10     11     12     13    14          15       16           17         18           19        20
    # columns: id | Section | CalculationNum | Drop | Point | No1c | No2c | No3c | No4c | No5c | No6c | No7c | No8c | No9c | RMS | Back_type | Stress | minus1_arr | null_arr | minus1_arr | null_arr
    points_drops = np.array(mde["deflections_calc"][:, 3:5])
    #            0          1         2               3         4        5      6    7    8    9   10   11   12   13   14   15        16               17     18     19           20         21           22        23         
    # columns: id | Chainage | TheTime |  Temperature2 | Drop No | Stress | Load | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | PointNo | AirTemperature | gpsx | gpsy | minus1_arr | null_arr | minus1_arr | null_arr
    deflections_all = np.array(mde["deflections"])
    deflections = np.array([tmp for tmp in deflections_all if(list(map(int, tmp[[4,16]])) in points_drops.tolist())])
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
    tempcorr, adj_elm, pcc_mod, rxn_subg = writeAndExecute(mde, pavtype, roadtype, ll_obj, sensordata)
    tmp = tempcorr*sensordata[:, 0]
    sensordata = np.insert(sensordata, 0, tmp, axis = 1)
    sensordata = np.round(sensordata, decimals = 2)
    load = np.reshape(load, (load.shape[0],))
    pressure = np.reshape(pressure, (pressure.shape[0],))
    pressure_for_calc = np.array(pressure.shape[0]*[82.06])
    pressure_for_calc = np.reshape(pressure_for_calc, (pressure.shape[0],))
    
    cal_obj = mr.cal_mr_sn(sensordata,pressure_for_calc, load, thickness)
    cal_obj.main_cal()
    return deflections, sensordata, pressure, load, cal_obj, point, drop_no, adj_elm, pcc_mod, rxn_subg


def getInvalidSections(mde, calc_data, d0crit, subgdcrit, pavtype):
    sensordata = calc_data["sensordata"]
    invalid_table = []
    new_stats = {"e1": [], "e2": [], "sn": [], "mr": [], "cbr": [], "k": []}
    for i in range(sensordata.shape[0]):
        # if(sensordata[i][0] > d0crit or sensordata[i][0] < subgdcrit):
        if(sensordata[i][0] > d0crit):
            drop_no = calc_data["drop_no"][i]
            point = calc_data["point"][i]
            if(pavtype == "concrete"):
                e1 = 0
                e2 = calc_data["e"][0][i]
            elif(pavtype == "asphalt"):
                e2 = 0
                e1 = calc_data["e"][0][i]
            else:
                e1 = calc_data["e"][0][i]
                e2 = calc_data["e"][1][i]
            chainage = None
            chainage2 = None
            for j in range(np.shape(mde["deflections"])[0]):
                if(int(mde["deflections"][j][4]) == int(drop_no) and int(mde["deflections"][j][16]) == int(point)):
                    chainage = mde["deflections"][j][1]
                    if((j+2) < np.shape(mde["deflections"])[0]):
                        chainage2 = mde["deflections"][j+2][1]
                    else:
                        chainage2 = chainage + 320
                    break
            invalid_table.append([round(float(chainage)*3.281), round(float(chainage2)*3.281)-1, abs((round(float(chainage2)*3.281)-1-round(float(chainage)*3.281))), e1, e2])
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
            new_stats["mr"].append(calc_data["insitumr"][i])
            new_stats["cbr"].append(calc_data["cbrarr"][i])
            new_stats["k"].append(calc_data["pcc_mod"][i])
    return invalid_table, new_stats

def writeAndExecute(mde, pavtype, roadtype, ll_obj, sensordata):
    writeLCC(mde, pavtype)
    writeLCC0()
    writeLCC1(roadtype, pavtype, ll_obj)
    writeELMOD_FWD(mde, sensordata)
    retcode = subprocess.call("C:/Aashto/YGJ.exe")
    if retcode != 0:
        raise Exception("YGJ.exe failed with return code {}. Check C:/Aashto/ input files.".format(retcode))
    temp_corr = None
    adj_elm = None
    with open("C:/Aashto/RESULT.dat") as f:
        line = f.readline()
        line = f.readline()
        adj_elm = float(line.split()[-1])
        line = f.readline()
        temp_corr = float(line.split()[1])

    with open("C:/Aashto/K_value.dat") as f:
        line = f.readline()
        pcc_mod = []
        rxn_subg = []
        line = f.readline()
        while(len(line.split()) != 0):
            pcc_mod.append(float(line.split()[1]))
            rxn_subg.append(float(line.split()[2]))
            line = f.readline()

    return temp_corr, adj_elm, pcc_mod, rxn_subg
        

def calc(con, id, pavtype, roadtype, ll_obj, mde, args):
    special_case = args.pavtype_special_case
    deflections, sensordata, pressure, load, cal_obj, point, drop_no, adj_elm, pcc_mod, rxn_subg = get_data(mde, pavtype, roadtype, ll_obj)
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
    subgd_calc = 10**(logmr_again*reg_line[0]+reg_line[1])
    e = get_E(mde, pavtype, adj_elm, special_case)

    sensor_stats = getstats(sensordata)
    mr_stats = getstats(mr)
    sn_stats = getstats(sn)
    cbr_stats = getstats(cbrarr)
    aash_esals_stats = getstats(aash_esals)
    ind_esals_stats = getstats(ind_esals)
    lim_esals_stats = getstats(lim_esals)
    insitu_mr_stats = getstats(insitumr)
    d0crit = getSurfaceDefCrit(mde)
    hmeans = {"sn": sn_stats[4], "remesals": lim_esals_stats[4], "mod_res": insitu_mr_stats[4]}
    esals_sheet = getESALS_reliability(hmeans, pavtype)
    misc = mde["misc"][0]
    misc = np.append(misc, esals_sheet["estimated psi"])
    misc = np.append(misc, esals_sheet["baseline esals"])
    misc = np.append(misc, esals_sheet["esal 95"])
    misc = np.append(misc, esals_sheet["esal 90"])
    misc = np.append(misc, esals_sheet["esal 80"])
    mde["misc"] = [misc]
    calc_data = {"e": e, "drop_no": drop_no, "point": point, "sensordata": sensordata, "mr": mr, "sn": sn, "aash_esals": aash_esals, "ind_esals": ind_esals, "lim_esals": lim_esals, "insitumr": insitumr, "logsgd": logsgd, "logmr": logmr, "cbrarr": cbrarr, "pressure": pressure, "load": load, "pcc_mod": pcc_mod, "rxn_subg": rxn_subg, "esals_sheet": esals_sheet}
    stats_data = {"sensorstats": sensor_stats, "mr_stats": mr_stats, "sn_stats": sn_stats, "cbr_stats": cbr_stats, "aash_esals": aash_esals_stats, "ind_esals": ind_esals_stats, "lim_esal": lim_esals_stats, "insitumr": insitu_mr_stats, "subgd_calc": subgd_calc, "d0crit": d0crit}
    invalid_table = []
    new_stats = []
    if(pavtype!="asphalt" and (not special_case)):
        invalid_table, new_stats = getInvalidSections(mde, calc_data, d0crit, subgd_calc, pavtype)
    calc_data["invalid_table"] = invalid_table
    calc_data["new_stats"] = new_stats
    return calc_data, stats_data, mde, pcc_mod, rxn_subg
