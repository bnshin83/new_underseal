import os
import statistics

def process_file(input_file_path):
    output_file_path = os.path.join(os.path.dirname(input_file_path), os.path.basename(input_file_path).replace('.f25', '_LTE_calculations.csv', 1).replace('.F25', '_LTE_calculations.csv', 1))

    # List to store all the LTE values for statistical analysis
    lte_values = []

    with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
        lines = input_file.readlines()
        i = 0
        
        output_file.write("Entry ID,3rd Entry,4th Entry,LTE\n")
        
        while i < len(lines):
            if lines[i].startswith("5303"):
                if i + 2 < len(lines) and i - 2 >= 0:
                    # Get the 6th item from the 5301 line
                    item_5301 = lines[i - 2].strip().split(",")[5]
                    
                    next_line = lines[i + 2].strip()
                    entries = next_line.split(",")
                    if len(entries) >= 4:
                        try:
                            third_entry = float(entries[2])
                            fourth_entry = float(entries[3])
                            if third_entry != 0:
                                result = (fourth_entry / third_entry) * 100
                                result = min(result, 100)
                                lte_values.append(result)
                                output_file.write(f"{item_5301},{third_entry},{fourth_entry},{result:.2f}\n")
                        except ValueError:
                            pass
            i += 1

        # Calculate and write the statistical analysis results to the file
        if lte_values:
            average_lte = statistics.mean(lte_values)
            std_dev_lte = statistics.stdev(lte_values)
            
            output_file.write(f"\nAverage LTE,{average_lte:.2f}\n")
            output_file.write(f"Standard Deviation,{std_dev_lte:.2f}\n")

    print(f"The modified file has been saved to {output_file_path}")

# Get the input file paths
input_file_paths = input("Please enter the file paths, separated by commas: ").split(',')

# Process each file
for input_file_path in input_file_paths:
    process_file(input_file_path.strip())
