import pyodbc
import db
import excel
import os
import pandas as pd
import numpy as np
import shutil
from match_images import match_image_chainage

def getGPS(f25_path):
    """
    Use dictionary to replace duplicated test point data (with identical chainage) with information from the most recent test point.
    """
    f25file = open(f25_path, "r")
    lines = f25file.readlines()
    # Filter out empty lines (lines containing only newline characters)
    lines = [line for line in lines if line.strip()]
    gpsx = []
    gpsy = []
    tmpgpsx = None
    tmpgpsy = None
    gpsx_dict, gpsy_dict = {}, {}

    # reading starts from line 40 in F25
    i = 40
    while i<len(lines):
        # Add more constraint to read gps data
        # if there are trouble reading the header number, skip the line
        try:
            header_num = int((lines[i].split(',')[0]))
        except:
            header_num = None
            raise Exception("Error occurs when extracting header number at line {}".format(i+1))
        
        if header_num == 5280:
            line_split_5280 = lines[i].split(',')
            tmpgpsx = float(line_split_5280[3])
            tmpgpsy = float(line_split_5280[4])
            if tmpgpsx<37 or tmpgpsx>43 or tmpgpsy<-89 or tmpgpsy>-84:
                tmpgpsx = None
                tmpgpsy = None
            i += 1 
            # Confirm chainage exists
            line_split = lines[i].split(',')
            if int(line_split[0]) == 5301:
                # Assume chainages are int
                try:
                    chainage = int(line_split[5])
                except:
                    raise Exception("Failed to convert chainage to int type at line {} in F25 file. "
                                    "Expected to extract chainage info from line starting with 5301, "
                                    "but the information is missing.".format(i+1))
                i += 3
                drop_no = 1
                # Only append the gps data if the first int of next line after 5303 is equal to drop number
                while(i<len(lines) and int((lines[i].split(',')[0]))==drop_no):
                    if drop_no == 1:
                        # Ensure latest info overwrite previous ones
                        gpsx_dict[chainage] = tmpgpsx
                        gpsy_dict[chainage] = tmpgpsy
                    i += 1
                    drop_no += 1
        else:
            i += 1
    
    # doing for loop outside the while to ensure 
    # the same gps is filled to all 3 drops even if the drop number in f25 is short of 3
    for chainage in gpsx_dict.keys():
        gpsx.extend([gpsx_dict[chainage]]*3)
        gpsy.extend([gpsy_dict[chainage]]*3)

    f25file.close()

    return gpsx, gpsy, gpsx_dict, gpsy_dict

def fill_missing_gps(gpsx_dict,gpsy_dict,df):
    filled_gps_x, filled_gps_y= [], []
    chainage_list = df['Chainage'].tolist()
    for chainage in chainage_list:
        chainage = int(chainage)
        # Fill gpsx
        if chainage not in gpsx_dict:
            filled_gps_x.append(None)
        else:
            filled_gps_x.append(gpsx_dict[chainage])
        # Fill gpsy
        if chainage not in gpsy_dict:
            filled_gps_y.append(None)
        else:
            filled_gps_y.append(gpsy_dict[chainage])
    return filled_gps_x, filled_gps_y


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
    f25file.close()
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

def read_mde(con, path, f25_path, id, ll_obj, gpsx, gpsy, gpsx_dict, gpsy_dict, args):
    """
    reuse the gpsx and gpsy that has been extracted at the begining of the result uploading
    """
    server_root = args.server_root
    skip_img_matching = args.skip_img_matching
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
    mde_conn = pyodbc.connect(driver_str)

    ########################################################################
    #Read and write to deflections
    df = pd.read_sql('select * from Deflections ORDER BY PointNo ASC, `Drop No` ASC', mde_conn)
    # Remove the duplicate (chainage, drop no.)
    # There will be no missing drops becuase MDE will automatically fill missing drop with 0.
    df.drop_duplicates(subset=['Chainage', 'Drop No'], keep='last', inplace=True)
    # ### Check for mde duplicate
    # df_chaiange_list = df['Chainage'].tolist()
    # chainage_3_interval = df_chaiange_list[::3]
    # if len(chainage_3_interval) != len(set(df_chaiange_list)):
    #     ll_obj['mde_duplicate'] = True
    #     uniq = set()
    #     ll_obj['duplicate_chainage'] = set()
    #     for item in chainage_3_interval:
    #         if item in uniq:
    #             ll_obj['duplicate_chainage'].add(item)
    #         else:
    #             uniq.add(item)


    # INCLUDE IMAGE MATCHING HERE
    ### Image matching part ###
    if not skip_img_matching:
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
    
    # Fill null and -1 array according to new dataframe
    null_arr = df.shape[0]*[None]
    minus1_arr = df.shape[0]*[-1]
    # check for missing gps data and fill them with Null for now
    # case F25 missing
    if len(gpsx) != len(gpsy):
        raise Exception("length of GPSX does not equal to length of GPSY")
    if len(df['Chainage'].tolist()) != len(gpsx):
        gpsx, gpsy = fill_missing_gps(gpsx_dict,gpsy_dict,df)

    arr = [df.shape[0]*[id], df['Chainage'].tolist(), list(map(str,(df['TheTime'].tolist()))),\
           df['Temperature2'].tolist(), df['Drop No'].tolist(),df['Stress'].tolist(), df['Load'].tolist(),\
           df['D1'].tolist(), df['D2'].tolist(), df['D3'].tolist(), df['D4'].tolist(), df['D5'].tolist(),\
           df['D6'].tolist(), df['D7'].tolist(), df['D8'].tolist(), df['D9'].tolist(), df['PointNo'].tolist(),\
           df['AirTemperature'].tolist(), gpsx, gpsy, minus1_arr, null_arr, minus1_arr, null_arr]

    # Wen added this line
    # Debug when converting list inside list to numpy array
    for i,v in enumerate(arr):
        if (len(v)!=len(arr[0])):
            raise Exception('Unexpected Error! Elemetnt dimension does no match. Bad element at column {}, expect length of {} but get {}.'.format(i, len(arr[0]), len(v)))
            
    # why the shape change to (24,) not (309,24) after transpose? becuase gpsx and gpsy is of length 311.
    # The len(arr) = 24, len(arr[i]) = 309
    # arr = np.transpose(arr)
    # print('Shape before transpose: {}'.format(np.array(arr).shape))

    arr = np.array(arr).T
    mde["deflections"] = arr
    #########################################################################

    ########################################################################
    #Read and write to deflections_calc
    df = pd.read_sql('select * from DEFLECTIONS_MEASURED_CALCULATED ORDER BY Point ASC, Drop ASC', mde_conn)
    # If there are duplicate chainage, keep the later
    df.drop_duplicates(subset=['Chainage','Drop'], keep='last', inplace=True)
    # After getrid of the duplicate chainage, keep only drop 2
    df.drop_duplicates(subset=['Chainage'], keep='first', inplace=True)
    null_arr = df.shape[0]*[None]
    minus1_arr = df.shape[0]*[-1]
    # print("Minus1_arr")
    # print(minus1_arr)
    arr = [df.shape[0]*[id], df['Section'].tolist(), df['CalculationNum'].tolist(), df['Drop'].tolist(), df['Point'].tolist(), df['No1c'].tolist(), df['No2c'].tolist(), df['No3c'].tolist(), df['No4c'].tolist(), df['No5c'].tolist(), df['No6c'].tolist(), df['No7c'].tolist(), df['No8c'].tolist(), df['No9c'].tolist(), df['RMS'].tolist(), df['Back_type'].tolist(), df['Stress'].tolist(), minus1_arr, null_arr, minus1_arr, null_arr]
    # print(arr)
    arr = np.transpose(arr)
    mde["deflections_calc"] = arr
    #########################################################################

    ########################################################################
    #Read and write to moduli_estimated
    df = pd.read_sql('select * from MODULI_ESTIMATED ORDER BY PointNo ASC, Drop ASC', mde_conn)
    # If there are duplicate chainage, keep the later
    df.drop_duplicates(subset=['Chainage','Drop'], keep='last', inplace=True)
    # After getrid of the duplicate chainage, keep only drop 2
    df.drop_duplicates(subset=['Chainage'], keep='first', inplace=True)
    null_arr = df.shape[0]*[None]
    minus1_arr = df.shape[0]*[-1]
    arr = [df.shape[0]*[id], df['Drop'].tolist(), df['PointNo'].tolist(), df['H1'].tolist(), df['H2'].tolist(), df['H3'].tolist(), df['H4'].tolist(), df['h_eq_con'].tolist(), df['Bedrock'].tolist(), df['E1'].tolist(), df['E2'].tolist(), df['E3'].tolist(), df['E4'].tolist(), df['E5'].tolist(), df['C'].tolist(), df['n'].tolist(), df['Emean'].tolist(), df['RMS'].tolist(), df['Method'].tolist(), df['From drop'].tolist(), df['Back_type'].tolist(), minus1_arr, null_arr, minus1_arr, null_arr]
    # print(arr)
    arr = np.transpose(arr)
    mde["mod_est"] = arr
    #########################################################################

    ########################################################################
    #Read and write to misc
    df = pd.read_sql('select * from Geophone_Positions', mde_conn)
    null_arr = df.shape[0]*[None]
    minus1_arr = df.shape[0]*[-1]
    df2 = pd.read_sql('select * from PLATE_GEOPHONE', mde_conn)
    radius = [df2['RadiusOfPlate'][0]]
    units = getUnits(f25_path)
    arr = [df.shape[0]*[id], df['Geo1-X'].tolist(), df['Geo1-Y'].tolist(), df['Geo2-X'].tolist(), df['Geo2-Y'].tolist(), df['Geo3-X'].tolist(), df['Geo3-Y'].tolist(), df['Geo4-X'].tolist(), df['Geo4-Y'].tolist(), df['Geo5-X'].tolist(), df['Geo5-Y'].tolist(), df['Geo6-X'].tolist(), df['Geo6-Y'].tolist(), df['Geo7-X'].tolist(), df['Geo7-Y'].tolist(), df['Geo8-X'].tolist(), df['Geo8-Y'].tolist(), df['Geo9-X'].tolist(), df['Geo9-Y'].tolist(), radius, [units[0]], [units[1]], [units[2]], [units[3]], [base[0].lower()]]
    arr = np.transpose(arr)
    print("'arr' from mde['misc'] = arr", arr)
    mde["misc"] = arr
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
    