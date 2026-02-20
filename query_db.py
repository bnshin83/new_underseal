# This script contains Utils for database query

def get_ll_from_db(con, ll_no, year):
    cursor = con.cursor()
    cursor.execute("SELECT longlist_no FROM stda_longlist_info WHERE longlist_no = :1 AND year = :2",
                   [ll_no, year])
    for result in cursor:
        longlist_no = result[0]
    cursor.close()
    return longlist_no

def read_db(con, table_name, col_name, cond_name, cond_value, year):
    cursor = con.cursor()
    # table_name, col_name, cond_name are internal constants — not user input
    sqlstr = "SELECT {} FROM {} WHERE ({} = :1 AND year = :2)".format(col_name, table_name, cond_name)
    cursor.execute(sqlstr, [cond_value, year])
    for result in cursor:
        result_temp = result
        break
    cursor.close()
    return result_temp

def read_db_from_ll_no_year(con, table_name, col_name, ll_no, year):
    cursor = con.cursor()
    sqlstr = "SELECT {} FROM {} WHERE (longlist_no = :1 AND year = :2)".format(col_name, table_name)
    cursor.execute(sqlstr, [ll_no, year])
    for result in cursor:
        result_temp = result
        break
    cursor.close()
    return result_temp

def get_unique_ll_no_list(con, year):
    result_temp = []
    cursor = con.cursor()
    cursor.execute("SELECT DISTINCT longlist_no FROM stda_longlist_info WHERE year = :1", [year])
    for result in cursor:
        result_temp.append(result[0])
    cursor.close()
    return result_temp

def update_db(con, table_name, update_col, new_value, ll_no, year):
    cursor = con.cursor()
    sqlstr = "UPDATE {} SET {} = :1 WHERE (longlist_no = :2 AND year = :3)".format(table_name, update_col)
    cursor.execute(sqlstr, [new_value, ll_no, year])
    con.commit()
    cursor.close()

def update_pavtype(con, table_name, update_col, new_value, ll_no, year):
    cursor = con.cursor()
    sqlstr = "UPDATE {} SET {} = :1 WHERE (longlist_no = :2 AND year = :3)".format(table_name, update_col)
    cursor.execute(sqlstr, [new_value, ll_no, year])
    con.commit()
    cursor.close()
