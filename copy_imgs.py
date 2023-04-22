import os, shutil

source_folder = "D:/indot_proj/Underseal/result_folder/Image matching"
dist_folder = "D:/indot_proj/Underseal/result_folder/Image matching/dist_folder"

for req_id in os.listdir("D:/indot_proj/Underseal/result_folder/Image matching"):
    if not req_id.startswith('D'):
        continue
    for sub_folder in os.listdir(os.path.join(source_folder,req_id)):
        if 'LL' not in sub_folder:
            continue
        for img_folder in os.listdir(os.path.join(source_folder, req_id,sub_folder)):
            img_folder_path = os.path.join(source_folder, req_id,sub_folder,img_folder)
            if (not os.path.isdir(img_folder_path)) or ('Cam1' not in os.listdir(os.path.join(source_folder, req_id,sub_folder,img_folder))):
                continue
            # copy the img_folder to dist folder
            dist_path = os.path.join(dist_folder,req_id,sub_folder,img_folder)
            shutil.copy(img_folder_path,dist_path)


            

