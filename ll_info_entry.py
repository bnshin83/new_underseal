import pyodbc
import cx_Oracle
import db
import excel
import os
import datetime
import re

from log_config import get_logger
logger = get_logger('ll_info_entry')

def compose_ll_info_entry_string(row, xls_filename_year, combine_flag):
    """
    year is decided by reading the first two digits of the request number
    """

    if int(xls_filename_year)>2022 and not combine_flag:
        ll = {"llno": str(excel.return_value(row, 'LL')).strip(),
              "test status": str(excel.return_value(row, 'Status')).strip(),
              "req no": str(excel.return_value(row, 'RequestID')).strip(),
              "route": str(excel.return_value(row, 'Route')).strip(),
              "rp from": str(excel.return_value(row, 'fromRP')).strip(),
              "rp to": str(excel.return_value(row, 'toRP')).strip(),
              "des no": str(excel.return_value(row, 'PK')).strip(),
              "district": str(excel.return_value(row, 'District')).strip(),
              "traffic": str(excel.return_value(row, 'Traffic')).strip(),
              "contact person": str(excel.return_value(row, 'Requestor')).strip(),
              "date req": str(excel.return_value(row, 'DateReceived')).strip(),
              "date needed": str(excel.return_value(row, 'DateNeeded')).strip(),
              "comments": str(excel.return_value(row, 'Requestor Note')).strip(),
              "operator_comment": str(excel.return_value(row, 'OperatorComments')).strip(),
              "traffic_ctrl":str(excel.return_value(row, 'DateScheduled')).strip(),
              "operator": str(excel.return_value(row, 'Operators')).strip(),
            }

    elif int(xls_filename_year)<=2022:
        ll = {"llno": str(excel.return_value(row, 'Long List Number')).strip(),
              "test status": str(excel.return_value(row, 'Status')).strip(),
              "req no": str(excel.return_value(row, 'Request Number')).strip(),
              "route": str(excel.return_value(row, 'Route')).strip(),
              "rp from": str(excel.return_value(row, 'RP (from)')).strip(),
              "rp to": str(excel.return_value(row, 'RP (to)')).strip(),
              "des no": str(excel.return_value(row, 'Contract/Des/PK Number')).strip(),
              "district": str(excel.return_value(row, 'District')).strip(),
              "traffic": str(excel.return_value(row, 'Traffic (Trucks per day)')).strip(),
              "contact person": str(excel.return_value(row, 'Requested By')).strip(),
              "date req": str(excel.return_value(row, 'Date Requested')).strip(),
              "date needed": str(excel.return_value(row, 'Date Needed')).strip(),
              "comments": str(excel.return_value(row, 'Comments by requestor')).strip(),
              "operator_comment": str(excel.return_value(row, 'Operator comments')).strip(),
              "traffic_ctrl":str(excel.return_value(row, 'Traffic Control Scheduled (Put only single day)')).strip(),
              "operator": str(excel.return_value(row, 'Operator')).strip(),
        }

    # Correct the format of route
    pattern = r'(US|SR|I)\s?-?(\d+)'
    replacement = r'\1-\2'
    ll['route'] = re.sub(pattern, replacement, ll['route'])

    # extract year after request id is extracted
    year_2digits_str = re.findall(r'D(\d{2})', ll["req no"])[0]
    year_str = '20'+year_2digits_str
    ll["year"] = year_str

    return ll


def ll_info_entry(con, ll_info_df, ll_no_colname, ll_no, xls_filename_year, combine_flag):

    row = excel.return_ll_info_row(ll_info_df, ll_no_colname, ll_no)
    ll = compose_ll_info_entry_string(row, xls_filename_year, combine_flag)

    cursor = con.cursor()
    cursor.execute("""INSERT INTO stda_LONGLIST_INFO
        VALUES (NULL, :llno, :year, :req_no, :test_status, :route,
                :rp_from, :rp_to, :des_no, :district, :traffic,
                :contact_person, :traffic_ctrl, :operator,
                :operator_comment, :date_req, :date_needed, :comments,
                -1, NULL, -1, NULL)""",
        {'llno': int(ll['llno']), 'year': ll['year'],
         'req_no': ll['req no'], 'test_status': ll['test status'],
         'route': ll['route'], 'rp_from': ll['rp from'], 'rp_to': ll['rp to'],
         'des_no': ll['des no'], 'district': ll['district'],
         'traffic': ll['traffic'], 'contact_person': ll['contact person'],
         'traffic_ctrl': ll['traffic_ctrl'], 'operator': ll['operator'],
         'operator_comment': ll['operator_comment'],
         'date_req': ll['date req'], 'date_needed': ll['date needed'],
         'comments': ll['comments']})

    cursor.execute("""SELECT LONGLIST_INFO_ID FROM stda_LONGLIST_INFO
        WHERE LONGLIST_NO = :llno AND YEAR = :year AND REQUEST_NO = :req_no
        AND ROUTE = :route AND RP_FROM = :rp_from AND RP_TO = :rp_to
        AND CONTRACT_NO = :des_no AND DISTRICT = :district
        AND NAME = :contact_person AND OPERATOR = :operator
        AND DATE_REQ = :date_req AND DATE_NEED = :date_needed""",
        {'llno': int(ll['llno']), 'year': ll['year'],
         'req_no': ll['req no'], 'route': ll['route'],
         'rp_from': ll['rp from'], 'rp_to': ll['rp to'],
         'des_no': ll['des no'], 'district': ll['district'],
         'contact_person': ll['contact person'], 'operator': ll['operator'],
         'date_req': ll['date req'], 'date_needed': ll['date needed']})

    for result in cursor:
        logger.debug('Content of result: %s', result)
        ll_info_id = result[0]

    con.commit()
    cursor.close()
    return ll_info_id, ll
