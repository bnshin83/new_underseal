import db

def get_ll_from_db(con, ll_no, year):
    cursor = con.cursor()
    sqlstr = """SELECT longlist_no FROM stda_longlist_info
    WHERE (longlist_no={} AND year={})""".format(ll_no,year)

    cursor.execute(sqlstr)
    for result in cursor:
        longlist_no = result[0]
        
    cursor.close()
    return longlist_no 

def read_db(con, table_name, col_name, cond_name, cond_value, year):
    cursor = con.cursor()
    sqlstr = """SELECT {} FROM {} WHERE ({}={} AND year={})""".format(col_name, table_name, cond_name, cond_value, year)
    cursor.execute(sqlstr)
    # print('cond value:', cond_value)
    for result in cursor:
        result_temp = result
        # Break at the first iteration because the fields are the same
        break
    cursor.close()
    return result_temp

def read_db_from_ll_no_year(con, table_name, col_name, ll_no, year):
    cursor = con.cursor()
    sqlstr = """SELECT {} FROM {} WHERE (longlist_no={} AND year={})""".format(col_name, table_name, ll_no, year)
    cursor.execute(sqlstr)

    for result in cursor:
        result_temp = result
        # Break at the first iteration because the fields are the same
        break
    cursor.close()
    return result_temp

def get_unique_ll_no_list(con,year):
    result_temp = []
    cursor = con.cursor()
    sqlstr = """SELECT DISTINCT longlist_no FROM stda_longlist_info WHERE year={}""".format(year)
    cursor.execute(sqlstr)

    for result in cursor:
        result_temp.append(result[0])
    cursor.close()
    return result_temp

def update_db(con,table_name, update_col, new_value, ll_no, year):
    cursor = con.cursor()
    sqlstr = """UPDATE {}
                SET {}='{}'
                WHERE (longlist_no={} AND year={})""".format(table_name, update_col, new_value.replace("'","''"), ll_no, year)
    # print(sqlstr)
    cursor.execute(sqlstr)
    con.commit()
    cursor.close()

def update_pavtype(con,table_name, update_col, new_value, ll_no, year):
    cursor = con.cursor()
    sqlstr = """UPDATE {}
                SET {}='{}'
                WHERE (longlist_no={} AND year={})""".format(table_name, update_col, new_value, ll_no, year)
    # print(sqlstr)
    cursor.execute(sqlstr)
    con.commit()
    cursor.close()