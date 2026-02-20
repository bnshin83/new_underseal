import os

def process_file(input_file_path):
    # Get the base name and extension of the input file
    base_name, ext = os.path.splitext(input_file_path)

    # Variables to store different sections of the file
    header_lines = []
    midslab_blocks = []
    joint_crack_blocks = []
    code_7901_lines = []
    current_block = []
    current_block_type = None

    with open(input_file_path, "r") as input_file:
        for line in input_file:
            if line.startswith(tuple(f"50{str(i).zfill(2)}" for i in range(45))):  
                header_lines.append(line)
                continue

            if line.startswith("7901"):  
                code_7901_lines.append(line)
                continue

            if line.startswith("7652"):  
                if current_block_type is not None:
                    if current_block_type == "Midslab":
                        midslab_blocks.extend(current_block)
                    else:
                        joint_crack_blocks.extend(current_block)
                    current_block = []
                current_block_type = "Midslab"
                current_block.append(line)
                continue

            if line.startswith("7654"):  
                if current_block_type is not None:
                    if current_block_type == "Midslab":
                        midslab_blocks.extend(current_block)
                    else:
                        joint_crack_blocks.extend(current_block)
                    current_block = []
                current_block_type = "Joint/Crack"
                current_block.append(line)
                continue

            if current_block_type is not None:
                current_block.append(line)

        # Add the last block to the respective list
        if current_block_type == "Midslab":
            midslab_blocks.extend(current_block)
        else:
            joint_crack_blocks.extend(current_block)

    # Write to the output files
    with open(base_name + "_output_joint_crack.f25", "w") as output_joint_crack, open(base_name + "_output_midslab.f25", "w") as output_midslab:
        output_joint_crack.writelines(header_lines + joint_crack_blocks + code_7901_lines)
        output_midslab.writelines(header_lines + midslab_blocks + code_7901_lines)

# Get the input file paths
input_file_paths = input("Please enter the file paths, separated by commas: ").split(',')

# Process each file
for input_file_path in input_file_paths:
    input_file_path = input_file_path.strip()
    if os.path.exists(input_file_path):
        process_file(input_file_path)
    else:
        print(f"The file path '{input_file_path}' does not exist.")
