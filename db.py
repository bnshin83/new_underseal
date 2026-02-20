# For no 'cx_Oracle' module error, use Power Shell not cmd
import copy
import cx_Oracle
import numpy as np
import sys, os

# Database credentials are loaded from environment variables.
# Set these before running:
#   UNDERSEAL_DEV_WEN_PASSWORD   (for dev_wen)
#   UNDERSEAL_ECN_PASSWORD       (for ecn_wen and ecn_shin)
#   UNDERSEAL_SHIN_PASSWORD      (for shin / production)

def connect(dev_env):
    if dev_env=='dev_wen':
        pw = os.environ.get('UNDERSEAL_DEV_WEN_PASSWORD')
        if not pw:
            raise Exception("Set UNDERSEAL_DEV_WEN_PASSWORD environment variable")
        cx_Oracle.init_oracle_client(lib_dir=r"D:\ChromeDownload\instantclient_19_14")
        con = cx_Oracle.connect(user='c##wen', password=pw, dsn="localhost:1522/orcl")
    elif dev_env in ('ecn_wen', 'ecn_shin'):
        pw = os.environ.get('UNDERSEAL_ECN_PASSWORD')
        if not pw:
            raise Exception("Set UNDERSEAL_ECN_PASSWORD environment variable")
        dsn = """
                (DESCRIPTION =
                  (ADDRESS_LIST =
                    (ADDRESS =
                      (PROTOCOL = TCP)
                      (HOST = oracle.ecn.purdue.edu)
                      (PORT = 1521)
                    )
                  )
                  (CONNECT_DATA =
                    (sid = primary)
                    (SERVICE_NAME = primary.ecn.purdue.edu)
                  )
                )
              """
        if dev_env == 'ecn_wen':
            cx_Oracle.init_oracle_client(lib_dir=r"D:\ChromeDownload\instantclient_21_11")
        else:
            cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
        con = cx_Oracle.connect(user='SPR4450', password=pw, dsn=dsn)
    elif dev_env=='shin':
        pw = os.environ.get('UNDERSEAL_SHIN_PASSWORD')
        if not pw:
            raise Exception("Set UNDERSEAL_SHIN_PASSWORD environment variable")
        cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
        con = cx_Oracle.connect(user='stda', password=pw, dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
    else:
        raise Exception ("Invalid dev_env option")
    return con

def putcalc(con, data, id, pcc_mod, rxn_subg):
    sensordata = data["sensordata"]
    # print(sensordata)
    # print("PCC_MOD")
    # print(pcc_mod)
    # print("RXN_SUBG")
    # print(rxn_subg)
    if(len(pcc_mod) == 0):
        pcc_mod = np.array([sensordata.shape[0]*[-1]])
    else:
        pcc_mod = np.array([pcc_mod])
    if(len(rxn_subg) == 0):
        rxn_subg = np.array([sensordata.shape[0]*[-1]])
    else:
        rxn_subg = np.array([rxn_subg])
    idarr = np.array([sensordata.shape[0]*[id]])
    minus1_arr = np.array([sensordata.shape[0]*[-1]])
    null_arr = np.array([sensordata.shape[0]*[None]])
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
    tmparr = np.concatenate((tmparr, np.transpose(data["e"][0:4,:])), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose(pcc_mod)), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose(rxn_subg)), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose(minus1_arr)), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose(null_arr)), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose(minus1_arr)), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose(null_arr)), axis = 1)
    tmparr = np.concatenate((tmparr, np.transpose(data["e"][4:5,:])), axis = 1)
    
    # print("Shape of data['e']",data["e"].shape)
    
    # tmparr = np.transpose(tmparr)
    # print(tmparr.shape)
    arr = list(map(tuple, tmparr))
    # print(arr)
    cursor = con.cursor()
    # print(arr)
    cursor.executemany("INSERT INTO stda_CALCULATIONS VALUES (NULL, :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29, :30, :31, :32, :33, :34, :35)", arr) #30
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
        arr.append([id, label] + list(sensorstats[i]) + [-1, None, -1, None])


    arr.append([id, "mr"]+data["mr_stats"]+[-1, None, -1, None])
    arr.append([id, "sn"]+data["sn_stats"]+[-1, None, -1, None])
    arr.append([id, "cbr"]+data["cbr_stats"]+[-1, None, -1, None])
    arr.append([id, "aash_esals"]+data["aash_esals"]+[-1, None, -1, None])
    arr.append([id, "ind_esals"]+data["ind_esals"]+[-1, None, -1, None])
    arr.append([id, "lim_esals"]+data["lim_esal"]+[-1, None, -1, None])
    arr.append([id, "insitumr"]+data["insitumr"]+[-1, None, -1, None])
    # arr = np.transpose(arr)
    # print(np.shape(arr))
    arr = list(map(tuple, arr))
    # print(arr)
    cursor = con.cursor()
    cursor.executemany("INSERT INTO stda_STATS VALUES (NULL, :1, :2, :3, :4, :5, :6, :7, :8, :9,:10, :11)", arr)#7
    con.commit()
    cursor.close()

def putmde(con, mde, stats_data, id, commit=0):
    cursor = con.cursor()

    chainge_ft_arr = copy.deepcopy(mde["deflections"])
    chainge_ft_arr[:,1] = np.around(chainge_ft_arr[:,1].astype(np.double)*3.28084)
    arr = list(map(tuple, chainge_ft_arr))
    # print('MDE DEFLECTIONS: ')
    # print(mde["deflections"].shape)
    # print("Deflections: ")
    # print(arr)
    # print("Printing type")
    
    # print(arr[0][-1])
    # print((arr[0][-2]))
    # print((arr[0][-3]))
    # print((arr[0][-4]))
    # print(len(arr[0]))
    # try:
    # print("Entering data to deflections")
    # print(arr)
    # print(id)
    cursor.executemany("INSERT INTO stda_DEFLECTIONS VALUES (NULL, :1, :2, TO_TIMESTAMP(:3, 'YYYY-MM-DD HH24:MI:SS'), :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, CAST(:1 as INT), :22, CAST(:1 as INT), :24)", arr) #was till 20

    ##********************************************
    arr = list(map(tuple, mde["deflections_calc"]))
    # print("Entering data to deflections calc")
    cursor.executemany("INSERT INTO stda_CALCULATED_DEFLECTIONS VALUES (NULL, :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21)", arr)#17
    ##********************************************
    arr = mde['mod_est']
    arr = list(map(tuple, arr))
    # # Convert E1-E5 to psi unit
    # arr_psi = mde['mod_est']
    # for i in range(9,13+1):
    #     arr_psi[:,i] = np.around(arr_psi[:,i].astype(np.double)*1000)
    # arr = list(map(tuple, arr_psi))
    # print("Entering data to mod est")
    cursor.executemany("INSERT INTO stda_MODULI_ESTIMATED VALUES (NULL, :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25)", arr)#21
    ##********************************************
    # print(mde["misc"])
    arr = mde["misc"][0]
    arr = np.append(arr, stats_data["d0crit"])
    arr = np.append(arr, stats_data["subgd_calc"])
    arr = np.append(arr, [-1])
    arr = np.append(arr, [None])
    arr = np.append(arr, [-1])
    arr = np.append(arr, [None])
    # arr = np.transpose(arr)
    mde["misc"] = [arr]
    arr = list(map(tuple, mde["misc"]))
    # print("Printing misc")
    # print(arr)
    # print("Entering data to misc")
    cursor.executemany("INSERT INTO stda_MISC VALUES (NULL, :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29, :30, :31, :32, :33, :34, :35, :36)", arr)#30
    ##********************************************
    if commit:
        con.commit()
    cursor.close()
    return

def putimg(con, ll_obj, id, year, lane_type, commit=0):

    cursor = con.cursor()

    request_id, dir = ll_obj['req no'], ll_obj['dir']

    img_dmi_dict = ll_obj['img_dmi_dict']

    # If there are matched images
    if img_dmi_dict:
        arr= []
        for image_filepath in img_dmi_dict:
            # For each row: (Request_id, Direction, DMI, Image path)
            img_url = 'https://resapps.indot.in.gov/photoviewer/data/FWD/' + image_filepath.replace('\\','/')
            row_temp = (id, request_id, dir, round(img_dmi_dict[image_filepath]*3.28084), img_url, -1, None, -1, None, lane_type)
            arr.append(row_temp)
        sql_str = "INSERT INTO stda_img VALUES (NULL, :1, :2, :3, :4, :5, CAST(:1 as INT), :7, CAST(:1 as INT), :9, :10)"
        cursor.executemany(sql_str, arr)
        if commit:
            con.commit()
        cursor.close()
    # if no match
    else:
        pass
    return