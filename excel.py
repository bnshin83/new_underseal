# These Excel utils functions are compatible with both 2022 and 2023 excel layout

import pandas as pd

def return_row(path, ll, worksheet = "Test Request Overview",ll_col_name='Long List Number'):
    df = pd.read_excel(path, sheet_name = worksheet)
    # print("Reached return_row")
    return df.loc[df[ll_col_name]==ll]

def return_value(row, srch):
    # print("returning value")
    return row[srch].values[0]
