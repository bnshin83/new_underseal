import pyodbc
import cx_Oracle
import db
import excel
import os
import datetime

def compose_ll_info_entry_string(row, year):
    """
    year: In the format of 2022, 2023, ... (Type is string)
    """

    if int(year)>2022:
        ll = {"llno": str(excel.return_value(row, 'LL')),
              "year": year,
              "test status": str(excel.return_value(row, 'Status')),
              "req no": str(excel.return_value(row, 'RequestID')),
              "route": str(excel.return_value(row, 'Route')),
              "rp from": str(excel.return_value(row, 'fromRP')),
              "rp to": str(excel.return_value(row, 'toRP')),
              "des no": str(excel.return_value(row, 'PK')),
              "district": str(excel.return_value(row, 'District')),
              "traffic": str(excel.return_value(row, 'Traffic')),
              "contact person": str(excel.return_value(row, 'Requestor')),
              "date req": str(excel.return_value(row, 'DateReceived')),
              "date needed": str(excel.return_value(row, 'DateNeeded')),
              "comments": str(excel.return_value(row, 'Requestor Note')),
              "operator_comment": str(excel.return_value(row, 'OperatorComments')),
              "traffic_ctrl":str(excel.return_value(row, 'DateScheduled')),
              "operator": excel.return_value(row, 'Operators'),
            }
    elif int(year)<=2022:
        ll = {"llno": str(excel.return_value(row, 'Long List Number')),
              "year": year,
              "test status": str(excel.return_value(row, 'Status')),
              "req no": str(excel.return_value(row, 'Request Number')),
              "route": str(excel.return_value(row, 'Route')),
              "rp from": str(excel.return_value(row, 'RP (from)')),
              "rp to": str(excel.return_value(row, 'RP (to)')),
              "des no": str(excel.return_value(row, 'Contract/Des/PK Number')),
              "district": str(excel.return_value(row, 'District')),
              "traffic": str(excel.return_value(row, 'Traffic (Trucks per day)')),
              "contact person": str(excel.return_value(row, 'Requested By')),
              "date req": str(excel.return_value(row, 'Date Requested')),
              "date needed": str(excel.return_value(row, 'Date Needed')),
              "comments": str(excel.return_value(row, 'Comments by requestor')),
              "operator_comment": str(excel.return_value(row, 'Operator comments')),
              "traffic_ctrl":str(excel.return_value(row, 'Traffic Control Scheduled (Put only single day)')),
              "operator": excel.return_value(row, 'Operator'),
        }

    # Use double single quote to escape single quote in sqlstr like it is done in .replace("'","''")
    sqlstr = """INSERT INTO stda_LONGLIST_INFO
    VALUES (NULL, """ + str(ll["llno"]) + """, 
    '""" + year + """', 
    '""" + str(ll["req no"]) + """', 
    '""" + str(ll["test status"]) + """', 
    '""" + str(ll["route"]) + """', 
    '""" + str(ll["rp from"]) + """', 
    '""" + str(ll["rp to"]) + """', 
    '""" + str(ll["des no"]) + """', 
    '""" + str(ll["district"]) + """', 
    '""" + str(ll["traffic"]) + """',
    '""" + str(ll["contact person"]) + """',
    '""" + str(ll["traffic_ctrl"]) + """',
    '""" + str(ll["operator"]) + """',
    '""" + str(ll["operator_comment"]).replace("'","''") + """',
    '""" + str(ll["date req"]) + """',
    '""" + str(ll["date needed"]) + """',
    '""" + str(ll["comments"]).replace("'","''") + """',
    -1, NULL, -1, NULL)"""

    idstr = """SELECT LONGLIST_INFO_ID FROM stda_LONGLIST_INFO
    WHERE LONGLIST_NO=""" + str(ll["llno"]) + """ AND  
    YEAR='""" + year + """' AND  
    REQUEST_NO='""" + str(ll["req no"]) + """' AND 
    ROUTE='""" + str(ll["route"]) + """' AND 
    RP_FROM='""" + str(ll["rp from"]) + """' AND 
    RP_TO='""" + str(ll["rp to"]) + """' AND  
    CONTRACT_NO='""" + str(ll["des no"]) + """' AND
    DISTRICT='""" + str(ll["district"]) + """' AND
    NAME='""" + str(ll["contact person"]) + """' AND 
    OPERATOR='""" + str(ll["operator"]) + """' AND  
    DATE_REQ='""" + str(ll["date req"]) + """' AND 
    DATE_NEED='""" + str(ll["date needed"]) + """'
    """
    # print(sqlstr)
    return sqlstr, idstr, ll


def ll_info_entry(con, excel_path, year, ll):
    # print(excel.return_row(path,ll))
    if int(year)>2022:
        row = excel.return_row(excel_path, ll, worksheet="Sheet1", ll_col_name="LL")
    else:
        row = excel.return_row(excel_path, ll, worksheet="Test Request Overview", ll_col_name='Long List Number')
    cursor = con.cursor()
    # print(compose_ll_info_entry_string(row))
    sqlstr, idstr, llobj = compose_ll_info_entry_string(row, year)
    cursor.execute(sqlstr)
    cursor.execute(idstr)
    
    for result in cursor:
        print('Content of result: {}'.format(result))
        ll_info_id = result[0]
    
    con.commit()
    cursor.close()
    ## llobj is a dictionary
    return ll_info_id, llobj
