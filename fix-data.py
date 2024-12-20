import csv

# Input and output file names
input_file = 'output_files/gold_matchdata.csv'
output_file = 'output_files/gold_matchdata_fixed.csv'

# Open the input file for reading and the output file for writing
with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        # Remove the 5th column if the row has 5 columns
        if len(row) >= 5:
            row.pop(4)
        # Write the modified row to the output file
        writer.writerow(row)

print(f"Modified file saved as {output_file}")
