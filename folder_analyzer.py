#!/usr/bin/env python3
"""
Refined Folder Structure Analysis Script
----------------------------------------
This script:
1. Analyzes folder structure excluding "cam1" folders
2. Prioritizes folders with "unknown", "Waiting for thickness data", or "no_comment"
   that also do NOT contain .mde files
3. Finds other folders without .mde files that have .txt files in second-level subfolders
4. Saves results to a text file
"""

import os
import datetime
from collections import Counter, defaultdict

def analyze_folder_structure(file_handle, root_path, level=0, prefix="", base_level=0):
    """Recursively display folder structure with specific exclusions."""
    # Check if path exists
    if not os.path.exists(root_path):
        file_handle.write(f"Error: The specified path does not exist: {root_path}\n")
        return
    
    # Get items in the current directory
    try:
        items = os.listdir(root_path)
    except PermissionError:
        file_handle.write(f"{prefix}├── [Access Denied]\n")
        return
    except Exception as e:
        file_handle.write(f"Error listing directory: {e}\n")
        return
    
    # Filter out folders named "cam1" and image files
    filtered_items = []
    for item in sorted(items):
        item_path = os.path.join(root_path, item)
        
        # Skip folders named "cam1"
        if os.path.isdir(item_path) and item.lower() == "cam1":
            continue
            
        # Skip image files
        _, ext = os.path.splitext(item.lower())
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico']:
            continue
            
        filtered_items.append(item)
    
    # Process each filtered item
    for i, item in enumerate(filtered_items):
        # Build the full path
        item_path = os.path.join(root_path, item)
        
        # Determine if this is the last item
        is_last = (i == len(filtered_items) - 1)
        connector = "└── " if is_last else "├── "
        
        if os.path.isdir(item_path):
            # It's a directory
            file_handle.write(f"{prefix}{connector}{item}/\n")
            
            # Recursively display contents
            new_prefix = prefix + ("    " if is_last else "│   ")
            analyze_folder_structure(file_handle, item_path, level + 1, new_prefix, base_level + 1)
        else:
            # It's a file
            file_handle.write(f"{prefix}{connector}{item}\n")

def find_special_folders(root_path):
    """
    Finds special folders in this order of priority:
    1. Folders with "unknown", "Waiting for thickness data", or "no_comment" 
       in name or content AND that have no .mde files
    2. Other folders without .mde files that have .txt files in second-level subfolders
    """
    priority_folders = []
    secondary_folders = []
    
    # Priority keywords to look for
    priority_keywords = ["unknown", "Waiting for thickness data", "no_comment"]
    
    for root, dirs, files in os.walk(root_path):
        # Skip cam1 folders
        if "cam1" in dirs:
            dirs.remove("cam1")
        
        # First check if the folder has any .mde files
        has_mde = any(file.lower().endswith('.mde') for file in files)
        
        # Only proceed if there are NO .mde files
        if not has_mde:
            # Check if folder name contains priority keywords
            folder_name = os.path.basename(root)
            is_priority = any(keyword.lower() in folder_name.lower() for keyword in priority_keywords)
            
            # Check if any files in this folder contain priority keywords
            if not is_priority:
                for file in files:
                    if file.endswith('.txt'):
                        try:
                            with open(os.path.join(root, file), 'r', errors='ignore') as f:
                                content = f.read()
                                if any(keyword in content for keyword in priority_keywords):
                                    is_priority = True
                                    break
                        except:
                            # Skip files that can't be read
                            pass
            
            if is_priority:
                priority_folders.append(root)
                continue
                
            # Check for second condition: .txt in second level
            has_txt_in_second_level = False
            
            for sub_root, sub_dirs, sub_files in os.walk(root):
                if "cam1" in sub_dirs:
                    sub_dirs.remove("cam1")
                    
                # Calculate subfolder depth
                rel_path = os.path.relpath(sub_root, root)
                sub_depth = len(rel_path.split(os.sep)) if rel_path != '.' else 0
                
                if sub_depth == 2:  # Second-level subfolder
                    if any(file.lower().endswith('.txt') for file in sub_files):
                        has_txt_in_second_level = True
                        break
            
            if has_txt_in_second_level:
                secondary_folders.append(root)
    
    return priority_folders, secondary_folders

def main():
    folder_path = r"V:\FWD\Underseal\Data\2023\todo\ready"
    output_file = "refined_folder_analysis.txt"
    
    # Open the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Display basic info about the folder
        if os.path.exists(folder_path):
            try:
                f.write(f"Refined Folder Analysis for: {folder_path}\n")
                f.write("=================================================\n\n")
                
                # Find priority and secondary folders
                priority_folders, secondary_folders = find_special_folders(folder_path)
                
                # Display priority folders
                f.write("PRIORITY FOLDERS:\n")
                f.write("-----------------\n")
                f.write("Folders WITHOUT .mde files that contain 'unknown', 'Waiting for thickness data', or 'no_comment':\n\n")
                
                if priority_folders:
                    for folder in sorted(priority_folders):
                        rel_path = os.path.relpath(folder, folder_path)
                        if rel_path == '.':
                            f.write(f"- [Root folder]\n")
                        else:
                            f.write(f"- {rel_path}\n")
                else:
                    f.write("No priority folders found.\n")
                
                # Display secondary folders
                f.write("\n\nSECONDARY FOLDERS:\n")
                f.write("------------------\n")
                f.write("Other folders without .mde files that have .txt files in second-level subfolders:\n\n")
                
                if secondary_folders:
                    for folder in sorted(secondary_folders):
                        rel_path = os.path.relpath(folder, folder_path)
                        if rel_path == '.':
                            f.write(f"- [Root folder]\n")
                        else:
                            f.write(f"- {rel_path}\n")
                else:
                    f.write("No secondary folders found.\n")
                
                # Display full folder structure
                f.write("\n\nCOMPLETE FOLDER STRUCTURE:\n")
                f.write("-------------------------\n")
                f.write("(excluding cam1 folders and image files)\n\n")
                analyze_folder_structure(f, folder_path)
                    
            except Exception as e:
                f.write(f"Error analyzing folder: {e}\n")
                import traceback
                f.write(traceback.format_exc())
        else:
            f.write(f"Error: The specified path does not exist: {folder_path}\n")
    
    print(f"Analysis complete! Results saved to: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()