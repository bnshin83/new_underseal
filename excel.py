import pandas as pd

def test_func():
    df = pd.read_excel(".\excel_file.xlsx", sheet_name="Test Request Overview", header=None, skiprows=range(0,2), nrows=265, usecols="A:AR")
    # pd.set_option("display.max_rows", 2, "display.max_columns", None)
    # for i in range(0, df.shape[0]):
    #     for j in range(0, df.shape[1]):
    #         print(df[j][i], end="   ")
    #     print("\n")

def return_row(path=".\excel_file.xlsx", ll=1, worksheet = "Test Request Overview"):
    df = pd.read_excel(path, sheet_name = worksheet)
    # print("Reached return_row")
    return df.loc[df['Long List Number']==ll]

def return_value(row, srch):
    # print("returning value")
    return row[srch].values[0]

# return_row()

