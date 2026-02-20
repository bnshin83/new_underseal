import copy
import cx_Oracle
import numpy as np
import os, traceback
import pandas as pd
import db

from log_config import get_logger
logger = get_logger('fill_gps')

def put_gps(con, csv_path):
    """
    Read GPS data from csv file and fill the GPS columns
    """

    gps_df = pd.read_csv(csv_path)
    # convert dmi to feet
    gps_df["DMI"] = (round(3.28084*gps_df["DMI"])).astype(int)

    # Get the basename of csv path, this base name should match the F25 file name (exclude extension name)
    csv_basename = os.path.basename(csv_path)[:-8] # Assume it ends with " gps.csv" (notice that there is a white space)

    cursor = con.cursor()

    # Get the longlist id first
    cursor.execute("SELECT LONGLIST_ID FROM stda_longlist WHERE F25_INFO = :1", [csv_basename])
    id = None
    for result in cursor:
        id = result[0]
    
    if id==None:
        logger.warning("Cannot find a matching longlist ID for: %s", csv_path)
        with open(gps_upload_error_log,"a+") as f:
            print("Cannot find a matching longlist ID for the following input CSV file:",file=f)
            print(csv_path,file=f)
            print("Check if the csv name matches the F25 name",file=f)
    # Update begin latitude, begin longitude, end latitude, end longitude
    begin_gpsx,begin_gpsy = gps_df.sort_values(by=['DMI'],ascending=True).head(1)[["Latitude","Longitude"]].values[0]
    end_gpsx,end_gpsy = gps_df.sort_values(by=['DMI'],ascending=False).head(1)[["Latitude","Longitude"]].values[0]
    logger.info("begin_gpsx,begin_gpsy %s %s", begin_gpsx, begin_gpsy)
    cursor.executemany("""
                    UPDATE stda_longlist
                    SET begin_latitude = :begin_lat,
                        begin_longitude = :begin_lon,
                        end_latitude = :end_lat,
                        end_longitude = :end_lon
                    WHERE longlist_id = :id""", 
                    [{"begin_lat": begin_gpsx, "begin_lon": begin_gpsy, "end_lat": end_gpsx, "end_lon": end_gpsy, "id": id}])


    # Update gpsx and gpsy table in stda.calculations
    # Concatenate id column to array. After concat: column order [feet, latitude, longtitude, id]
    sql_arr = np.concatenate((np.array(gps_df), np.array([[id]]*gps_df.shape[0])), axis=1)
    # need to change column order to [latitude, longtitude, feet, id]
    sql_arr = sql_arr[:,[1,2,0,3]]
    sql_arr = list(map(tuple,sql_arr))

    query = """
            UPDATE stda_deflections
            SET gpsx = :gpsx_val,
                gpsy = :gpsy_val
            WHERE longlist_id = :longlist_id_val AND chainage_ft = :chainage_ft_val
            """

    cursor.executemany(query, [{"gpsx_val": sql_arr_row[0], 
                                "gpsy_val": sql_arr_row[1], 
                                "longlist_id_val": id, 
                                "chainage_ft_val": sql_arr_row[2]} 
                                for sql_arr_row in sql_arr])
    
    con.commit()
    cursor.close()


if __name__ == "__main__":
    
    import argparse
    from tkinter import filedialog

    parser = argparse.ArgumentParser(description='Upload misssing GPS data in batch mode')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--dev_env', type=str, default="shin",choices=['dev_wen', 'shin', 'ecn_wen','ecn_shin'])
    args = parser.parse_args()

    batch_csv_txt = filedialog.askopenfilename(initialdir='./',title='Select An External .txt File', 
                                          filetypes=(("TXT files","*.txt"),("all files","*.*"))
                                         )

    gps_upload_error_log = os.path.join(os.path.dirname(batch_csv_txt),"GPS_upload_error_log.txt")
    if os.path.exists(gps_upload_error_log):
        os.remove(gps_upload_error_log)

    con = db.connect(args.dev_env)

    with open(batch_csv_txt,'r') as file:
        Lines = file.readlines()

    from datetime import datetime
    logger.info("=" * 60)
    logger.info("RUN STARTED (fill_gps): %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    for line in Lines:
        csv_path = line.strip('\"')
        logger.info("csv_path: %s", csv_path)
        try:
            put_gps(con, csv_path)
            logger.info("Successfully upload %s", os.path.basename(csv_path))
        except Exception:
            traceback_str = traceback.format_exc()
            logger.error(traceback_str)
            with open(gps_upload_error_log,"a+") as f:
                print("######### Start of error log #########",file=f)
                print('Input CSV path: {}\n'.format(csv_path),file=f)
                print(traceback_str,file=f)
                print("######### End of error log #########\n\n",file=f)

    logger.info("RUN ENDED (fill_gps): %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("=" * 60)