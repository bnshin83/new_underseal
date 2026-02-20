import os, bisect, shutil
from collections import defaultdict

from log_config import get_logger
logger = get_logger('match_images')

def match_image_chainage(f25_path,ll_obj,df, server_root):
    """
    Need to know:
        1. F25 file name
        2. Request number: in ll_obj['req no']
        3. Chainage list: From 'df'. 'df' is from Delfection sheet of .mde, ordered by chainage(point number) and drop number.\
                          Match the chainage in 'df' with the chainage from the image filename
        4. Image path
        5. Image names

    Return: 
        1. Dict that matches chainage with image filename (if not succes -> None)
        2. Success flag
        3. Error message (if success -> None)
    """
    req_no = ll_obj['req no']
    ll_no_folder = os.path.dirname(f25_path)
    req_no_folder = os.path.dirname(ll_no_folder)
    f25_basename_no_extension_name = os.path.basename(f25_path)[:-4]

    find_ll_folder = False
    for sub_item in os.listdir(req_no_folder):
        ll_folder = os.path.join(req_no_folder,sub_item)
        if os.path.isdir(ll_folder) and ('LL' in sub_item or 'll' in sub_item):
            find_ll_folder = True
            lane_folders = set(os.listdir(ll_folder))
            if f25_basename_no_extension_name in lane_folders:
                lane_folder_path = os.path.join(ll_folder, f25_basename_no_extension_name)
                if "Cam1" in os.listdir(lane_folder_path):
                    cam_folder_path = os.path.join(lane_folder_path,"Cam1")
                    image_filenames = os.listdir(cam_folder_path)
                    relative_path = os.path.join(req_no,sub_item,f25_basename_no_extension_name,'Cam1')
                    dmi_img_dict, img_dmi_dict = get_chainage_imgname_dict(df,image_filenames,relative_path)
                    ### Copy images to INDOT server ###
                    # Use aboslute path
                    logger.info('Copying images ...')
                    source_path = os.path.join(ll_no_folder,f25_basename_no_extension_name,'Cam1')
                    # print('[Debug info]: source_path:{}'.format(source_path))
                    # server_root = "\\\\dotwebp016vw/data/FWD/"
                    dist_path = os.path.join(server_root,req_no,sub_item,f25_basename_no_extension_name,'Cam1')
                    # print('[Debug info]: dist_path:{}'.format(dist_path))
                    if not os.path.exists(dist_path):
                        os.makedirs(dist_path)
                        # Copy image by image, and change the extension name
                        for img_filename in os.listdir(source_path):
                            if img_filename.endswith('jpg'):
                                shutil.copy(os.path.join(source_path,img_filename), os.path.join(dist_path,img_filename))
                            elif img_filename.endswith('tif'):
                                from PIL import Image
                                im = Image.open(os.path.join(source_path, img_filename))
                                im.save(os.path.join(dist_path, img_filename[:-3]+'jpg'))
                                im.close()
                            else:
                                continue
                        # shutil.copytree(source_path,dist_path)
                    return dmi_img_dict, img_dmi_dict, True,None
                else:
                    return None, None, False,"(Images not matched) No 'Cam1' folder found."
            else:
                return None, None, False,'(Images not matched) No folder name matches the f25 file name.'
    if not find_ll_folder:
        return None, None, False,'(Images not matched) Sub item under the request folder should be a folder that contains LL no nad route.'

def ImageChainToChain(image_chain,chain):
    """
    Use Binary Search to find the closest chainage. 
    Match chainage extracted from image with Chainage for FWD points.

    Return:
        Chainage number that is matched to.
    """
    if chain[-1] < chain[0]:
        chain.reverse()
    insert_idx = bisect.bisect_left(chain, image_chain)
    if insert_idx == 0:
        return chain[0]
    # if the image chainage is larger than the largest chainage
    elif insert_idx == len(chain):
        return chain[-1]
    else:
        smaller_chain,larger_chain = chain[insert_idx-1], chain[insert_idx]
        if abs(smaller_chain-image_chain) <= abs(larger_chain-image_chain):
            return smaller_chain
        else:
            return larger_chain

def get_chainage_imgname_dict(df, image_filenames, relative_path):
    """
    Input:
        1. List of image names
        2. List of sorted chainage. But the chainage could be sorted in "small to large" or "large to small"
    
    Return:
        Dict that matches chainage with image filename
    """
    # The list is sorted by chainage already
    
    chainage_list = df['Chainage'].tolist()
    unique_chainage = list(set(chainage_list))
    unique_chainage.sort()
    # # Make sure every unique chainage is repeated 3 times, becuase we have 3 drops
    # assert len(set(chainage_list))==len(unique_chainage), "There is a mismatch in total number of drops, check MDE... Chainage List: {}".format(chainage_list)
    
    if len(unique_chainage) == 1:
        return {unique_chainage[0]:image_filenames}

    chainage_dict = defaultdict(list)
    img_dmi_dict = {}
    for image_filename in image_filenames:
        # skip non-image
        if image_filename.endswith('tif'):
            image_filename = image_filename[:-3]+'jpg'
        if image_filename.endswith('jpg'):
            try:
                img_chainage = float(image_filename.split(' ')[-2])
            except Exception:
                logger.warning('Cannot convert to float image_filename: %s', image_filename)
            matched_chainage = ImageChainToChain(img_chainage, unique_chainage)
            # print('img_dmi: {}, matched_dmi: {}'.format(img_chainage,matched_chainage))
            image_filepath = os.path.join(relative_path,image_filename)
            chainage_dict[matched_chainage].append(image_filepath)
            img_dmi_dict[image_filepath] = matched_chainage
    
    return chainage_dict, img_dmi_dict