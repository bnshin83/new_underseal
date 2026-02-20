
def get_joint_midslab_loc(f25_path):
    loc_dict = {}
    with open(f25_path,"r") as f:
        for line in f:
            line_split = line.split(',')
            if line_split[0] not in {'7652','7654'}:
                continue
            dmi = round(int(line_split[1])*3.28084)
            loc_dict[dmi] = line_split[2].strip().replace('"', '')
    return loc_dict


if __name__ == "__main__":
    
    import pandas as pd
    import argparse, os

    parser = argparse.ArgumentParser(description='Script for adding comments to Excel query results')
    parser.add_argument('--xls_path', type=str, required=True)
    parser.add_argument('--f25_folder', type=str, required=True)
    args = parser.parse_args()
    # convert the format
    args.xls_path = args.xls_path.replace("\\","/")
    args.f25_folder = args.f25_folder.replace("\\","/")
    args.xls_path = args.xls_path.replace('""','')
    args.f25_folder = args.f25_folder.replace('""','')

    df = pd.read_excel(args.xls_path, sheet_name = "export")
    df['joint/midslab'] = ['']*df.shape[0]
    df['TEST_DATE'] = pd.to_datetime(df['TEST_DATE'])
    df['TEST_DATE'] = df['TEST_DATE'].dt.strftime('%Y/%m/%d')
    filename_dict = {}
    for filename in df["Filename"].unique():
        f25_path = os.path.join(args.f25_folder, filename+".F25")
        if not os.path.exists(f25_path):
            print("Cannot find {}".format(f25_path))
            continue
        dmi_comment_dict = get_joint_midslab_loc(f25_path)
        filename_dict[filename] = dmi_comment_dict

    # loop over all the rows in Excel
    for index, row in df.iterrows():
        dmi = int(row['CHAINAGE'])
        filename = row['Filename']
        if filename in filename_dict and dmi in filename_dict[row['Filename']]:
            df.loc[index, 'joint/midslab'] = filename_dict[row['Filename']][dmi]
    
    orig_xls_name = os.path.basename(args.xls_path)
    orig_xls_folder = os.path.dirname(args.xls_path)
    output_path = os.path.join(orig_xls_folder,orig_xls_name[:-5]+"_with_loc.xlsx")
    df.to_excel(output_path,index=False)

    