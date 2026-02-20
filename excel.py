# These Excel utils functions are compatible with both 2022 and 2023 excel layout

import pandas as pd

def return_ll_info_row(ll_info_df, ll_no_col_name, req_no):
    return ll_info_df.loc[ll_info_df[ll_no_col_name]==req_no]

def return_value(row, srch):
    return row[srch].values[0]
