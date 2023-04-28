import pyodbc
import db
import excel
import os
import pandas as pd
import numpy as np
import shutil
from match_images import match_image_chainage

def getGPS(f25_path):
    f25file = open(f25_path, "r")
    lines = f25file.readlines()
    gpsx = []
    gpsy = []
    tmpgpsx = None
    tmpgpsy = None
    sum = 0
    for i in range(40, len(lines)):
        # Add more constraint to read gps data
        if(int((lines[i].split(',')[0])) == 5280):
            tmpgpsx = (float((lines[i].split(',')[3])))
            tmpgpsy = (float((lines[i].split(',')[4])))
        if(int((lines[i].split(',')[0])) == 5303):
            i = i+1
            if(int((lines[i].split(',')[0])) == 1):
                # Wen: modified this line
                # Only append the gps data if the first int of next line after 5303 is 1
                gpsx.append(tmpgpsx)
                gpsy.append(tmpgpsy)
                # print("hi")
                num = 1
                i = i + 1
                while( i < len(lines) and int((lines[i].split(',')[0])) == num + 1):
                    # print("hi2")
                    gpsx.append(gpsx[-1])
                    gpsy.append(gpsy[-1])
                    i = i+1
                    num = num + 1
                sum = sum+num
                # print(str(num), "Lines were taken")
                # print(str(sum), "is total lines taken till now")
                # print(len(gpsx), "*******", len(gpsy))
                i = i - 1
            
    # print(len(gpsx), "*******", len(gpsy))
    # print("gpsx: ", gpsx)
    # print("*************")
    # print("gpsy: ", gpsy)

    return gpsx, gpsy

def getUnits(f25_path):
    f25file = open(f25_path, "r")
    lines = f25file.readlines()
    units = []
    for line in lines:
        if(line.split(",")[0] == "5010"):
            arr = line.split(",")
            units.append("C" if arr[1] == "0" else "F")#Temperature
            units.append("kpa" if arr[10] == "0" else "psi")#Force
            units.append("micron" if arr[5] == "0" else "mil")#Deflection
            # units.append(arr[6])#distance
            if(arr[6] == "0"):
                units.append("mm")
            elif (arr[6] == "1"):
                units.append("inch")
            elif (arr[6] == "2"):
                units.append("meters")
            elif (arr[6] == "3"):
                units.append("km")
            elif (arr[6] == "4"):
                units.append("km extended")
            elif (arr[6] == "5"):
                units.append("feet")
            elif (arr[6] == "6"):
                units.append("yards")
            elif (arr[6] == "7"):
                units.append("miles")
            elif (arr[6] == "8"):
                units.append("miles extended")
            elif (arr[6] == "9"):
                units.append("miles.feet")
            break
    return units

def read_pavtype(path, f25_path):

    pre, ext = os.path.splitext(path)
    base = os.path.basename(f25_path)
    newpath = pre + '.accdb'
    shutil.copy(path, newpath)

    driver_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + str(newpath)
    mde_conn = pyodbc.connect(driver_str)
    df = pd.read_sql('select * from Thickness ORDER BY SectionID ASC', mde_conn)
    pav_e1 = df['e1'][0]
    # print("df['e1']:",mde['pav_e1'])
    pav_e2 = df['e2'][0]
    mde_conn.close()
    return pav_e1, pav_e2

def read_mde(con, path, f25_path, id, ll_obj, server_root, img_matching=True):
    mde = {}
    pre, ext = os.path.splitext(path)
    base = os.path.basename(f25_path)
    newpath = pre + '.accdb'
    shutil.copy(path, newpath)
    # if(ext == '.mde'):
    #     os.rename(path, pre + '.accdb')
    #     newpath = pre + '.accdb'
    # else:
    #     newpath = path
    cursor = con.cursor()
    # print("newpath: ", newpath)
    driver_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + str(newpath)
    # print("driver_str: ", driver_str)
    # print("IS THIS WHERE TEH ERROR IS")
    mde_conn = pyodbc.connect(driver_str)
    # print("IS THIS WHERE THE ERROR IS PART 2")
    ########################################################################
    #Read and write to deflections
    df = pd.read_sql('select * from Deflections ORDER BY PointNo ASC, `Drop no` ASC', mde_conn)
    ### Check for mde duplicate
    df_chaiange_list = df['Chainage'].tolist()
    chainage_3_interval = df_chaiange_list[::3]
    if len(chainage_3_interval) != len(set(df_chaiange_list)):
        ll_obj['mde_duplicate'] = True
        uniq = set()
        ll_obj['duplicate_chainage'] = set()
        for item in chainage_3_interval:
            if item in uniq:
                ll_obj['duplicate_chainage'].add(item)
            else:
                uniq.add(item)
    # print('mde df shape: {}'.format(df.shape))
    gpsx, gpsy = getGPS(f25_path)
    null_arr = df.shape[0]*[None]
    minus1_arr = df.shape[0]*[-1]
    # print('null_arr: {}'.format(null_arr))
    # print('minus1_arr: {}'.format( minus1_arr))

    # INCLUDE IMAGE MATCHING HERE
    ### Image matching part ###
    if img_matching:
        dmi_img_dict, img_dmi_dict, success_match, nomatch_message = match_image_chainage(f25_path, ll_obj, df, server_root)
        if success_match:
            imgnames_list = []
            for chainage in df['Chainage'].tolist():
                imgnames_list.append(",".join(dmi_img_dict[chainage]))
            # Save the DMI-->imgname dict to ll_obj
            ll_obj['dmi_img_dict'] = dmi_img_dict
            # Save the img-->DMI dict for STDA_IMG table
            ll_obj['img_dmi_dict'] = img_dmi_dict

        else:
            print(nomatch_message)
            ll_obj['nomatch_msg'] = nomatch_message
            ll_obj['dmi_img_dict'] = None
            ll_obj['img_dmi_dict'] = None
            imgnames_list = df.shape[0]*[None]
        ### Image matching part ###

    arr = [df.shape[0]*[id], df['Chainage'].tolist(), list(map(str,(df['TheTime'].tolist()))),\
           df['Temperature2'].tolist(), df['Drop No'].tolist(),df['Stress'].tolist(), df['Load'].tolist(),\
           df['D1'].tolist(), df['D2'].tolist(), df['D3'].tolist(), df['D4'].tolist(), df['D5'].tolist(),\
           df['D6'].tolist(), df['D7'].tolist(), df['D8'].tolist(), df['D9'].tolist(), df['PointNo'].tolist(),\
           df['AirTemperature'].tolist(), gpsx, gpsy, minus1_arr, null_arr, minus1_arr, null_arr]

    # Wen added this line
    # Debug when converting list inside list to numpy array
    for i,v in enumerate(arr):
        if (len(v)!=len(arr[0])):
            print('Output of col {}: {}'.format(i,v))
            raise Exception('element dimension does not match. Bad element at column {}, expect length of {} but get {}'.format(i, len(arr[0]), len(v)))
            

    # why the shape change to (24,) not (309,24) after transpose? becuase gpsx and gpsy is of length 311.
    # The len(arr) = 24, len(arr[i]) = 309
    # arr = np.transpose(arr)
    # print('Shape before transpose: {}'.format(np.array(arr).shape))

    arr = np.array(arr).T
    mde["deflections"] = arr
    # arr = list(map(tuple, arr))
    # # print("Arr array: ", arr)
    # cursor.executemany("INSERT INTO DEFLECTIONS VALUES (:1, :2, TO_TIMESTAMP(:3, 'YYYY-MM-DD HH24:MI:SS'), :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20)", arr)
    #########################################################################

    ########################################################################
    #Read and write to deflections_calc
    df = pd.read_sql('select * from DEFLECTIONS_MEASURED_CALCULATED ORDER BY Point ASC, Drop ASC', mde_conn)
    null_arr = df.shape[0]*[None]
    minus1_arr = df.shape[0]*[-1]
    # print("Minus1_arr")
    # print(minus1_arr)
    arr = [df.shape[0]*[id], df['Section'].tolist(), df['CalculationNum'].tolist(), df['Drop'].tolist(), df['Point'].tolist(), df['No1c'].tolist(), df['No2c'].tolist(), df['No3c'].tolist(), df['No4c'].tolist(), df['No5c'].tolist(), df['No6c'].tolist(), df['No7c'].tolist(), df['No8c'].tolist(), df['No9c'].tolist(), df['RMS'].tolist(), df['Back_type'].tolist(), df['Stress'].tolist(), minus1_arr, null_arr, minus1_arr, null_arr]
    # print(arr)
    arr = np.transpose(arr)
    mde["deflections_calc"] = arr
    # print("DEFLECTIONS CALC SHAPE", str(np.shape(mde["deflections_calc"])))
    # arr = list(map(tuple, arr))
    # cursor.executemany("INSERT INTO DEFLECTIONS_CALC VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17)", arr)
    #########################################################################

    ########################################################################
    #Read and write to moduli_estimated
    df = pd.read_sql('select * from MODULI_ESTIMATED ORDER BY PointNo ASC, Drop ASC', mde_conn)
    null_arr = df.shape[0]*[None]
    minus1_arr = df.shape[0]*[-1]
    arr = [df.shape[0]*[id], df['Drop'].tolist(), df['PointNo'].tolist(), df['H1'].tolist(), df['H2'].tolist(), df['H3'].tolist(), df['H4'].tolist(), df['h_eq_con'].tolist(), df['Bedrock'].tolist(), df['E1'].tolist(), df['E2'].tolist(), df['E3'].tolist(), df['E4'].tolist(), df['E5'].tolist(), df['C'].tolist(), df['n'].tolist(), df['Emean'].tolist(), df['RMS'].tolist(), df['Method'].tolist(), df['From drop'].tolist(), df['Back_type'].tolist(), minus1_arr, null_arr, minus1_arr, null_arr]
    # print(arr)
    arr = np.transpose(arr)
    mde["mod_est"] = arr
    # arr = list(map(tuple, arr))
    # cursor.executemany("INSERT INTO MOD_EST VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21)", arr)
    #########################################################################

    ########################################################################
    #Read and write to misc
    df = pd.read_sql('select * from Geophone_Positions', mde_conn)
    null_arr = df.shape[0]*[None]
    minus1_arr = df.shape[0]*[-1]
    # print("Misc null")
    # print(null_arr)
    # print("Misc minus1")
    # print(minus1_arr)
    df2 = pd.read_sql('select * from PLATE_GEOPHONE', mde_conn)
    radius = [df2['RadiusOfPlate'][0]]
    units = getUnits(f25_path)
    arr = [df.shape[0]*[id], df['Geo1-X'].tolist(), df['Geo1-Y'].tolist(), df['Geo2-X'].tolist(), df['Geo2-Y'].tolist(), df['Geo3-X'].tolist(), df['Geo3-Y'].tolist(), df['Geo4-X'].tolist(), df['Geo4-Y'].tolist(), df['Geo5-X'].tolist(), df['Geo5-Y'].tolist(), df['Geo6-X'].tolist(), df['Geo6-Y'].tolist(), df['Geo7-X'].tolist(), df['Geo7-Y'].tolist(), df['Geo8-X'].tolist(), df['Geo8-Y'].tolist(), df['Geo9-X'].tolist(), df['Geo9-Y'].tolist(), radius, [units[0]], [units[1]], [units[2]], [units[3]], [base[0].lower()]]
    arr = np.transpose(arr)
    # print(arr)
    mde["misc"] = arr
    # arr = list(map(tuple, arr))
    # cursor.executemany("INSERT INTO MISC VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25)", arr)
    #########################################################################

    ########################################################################
    #Read and write thickness sheet and get e1, e2 to estimate the pavement type
    df = pd.read_sql('select * from Thickness ORDER BY SectionID ASC', mde_conn)
    mde['pav_e1'] = df['e1'][0]
    # print("df['e1']:",mde['pav_e1'])
    mde['pav_e2'] = df['e2'][0]
    # print('MDE e1 type:',type(mde['pav_e1']))

    # con.commit()
    cursor.close()
    mde_conn.close()
    return mde, base[0].lower(), base.split()[0], ll_obj
    
    

# read_mde(db.connect(), './test.accdb', 'SR-17 NB RP-47+18 to RP-50+41.F25', 2)
# init_mde_tables(db.connect())
# connect_sqlalchemy()