import os

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
        # new_f25_path = f25_path[:-4] + '_new.F25'
        with open(f25_path, "w") as f:
            f.writelines(lines)

        print('Modified F25 saved in: {}'.format(f25_path))
    
    


if __name__ =='__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Fix the format issue of f25 file')
    parser.add_argument('-p','--path', type=str, required=False, default=None)
    parser.add_argument('--root_folder', type=str, required=False, default=None)
    args = parser.parse_args()

    if args.path is not None:
        correct_f25_format(args.path)
    
    if args.root_folder is not None:
        for req_id in os.listdir(args.root_folder):
            if not req_id.startswith('D'):
                continue
            for subfolder in os.listdir(os.path.join(args.root_folder,req_id)):
                if 'LL' not in subfolder or not os.path.isdir(os.path.join(args.root_folder,req_id,subfolder)):
                    continue
                for f25_file in os.listdir(os.path.join(args.root_folder,req_id,subfolder)):
                    if not f25_file.endswith('.F25'):
                        continue
                    # if it ends with F25
                    f25_full_path = os.path.join(args.root_folder,req_id,subfolder,f25_file)
                    correct_f25_format(f25_full_path)
