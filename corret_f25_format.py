import db
import excel
import os
import pandas as pd
import numpy as np
import shutil

def correct_f25_format(f25_path):
    f25file = open(f25_path, "r")
    lines = f25file.readlines()
    format_error_flag = 0
    for line_idx in range(len(lines)):
        temp_line = lines[line_idx].split(',')
        first_number = temp_line[0]
        if int(first_number) in {1,2,3} and len(first_number)!=4:
            if format_error_flag == 0:
                print('Format error of F25 found...')
                format_error_flag = 1
            temp_line[0] = '   {}'.format(int(first_number)) # add 3 spaces in front
            lines[line_idx] = ",".join(temp_line)

    if format_error_flag:
        new_f25_path = f25_path[:-4] + '_new.F25'
        with open(new_f25_path, "w") as f:
            f.writelines(lines)

        print('Modified F25 saved in: {}'.format(new_f25_path))
    
    


if __name__ =='__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Fix the indention issue of f25 file')
    parser.add_argument('-p','--path', type=str, required=True)
    args = parser.parse_args()

    correct_f25_format(args.path)