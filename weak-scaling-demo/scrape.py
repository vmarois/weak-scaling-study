# Import modules
import readline, glob
import csv
from itertools import izip

# Available options for x-value - keyboard input
x_str_list = ['Cores', 'Degrees-of-freedom', 'Degrees-of-freedom-per-core']

def completex(text, state):
    for cmd in x_str_list:
        if cmd.startswith(text):
            if not state:
                return cmd
            else:
                state -= 1

readline.parse_and_bind("tab: complete")
readline.set_completer(completex)
x_inp = raw_input('Enter x-value to extract: ')

# Available options for y-value - keyboard input
y_str_list=['Assemble', 'Create-Mesh', 'DirichletBC', 'FunctionSpace',
            'PETSC-options', 'Solve']

def completey(text, state):
    for cmd in y_str_list:
        if cmd.startswith(text):
            if not state:
                return cmd
            else:
                state -= 1

readline.parse_and_bind("tab: complete")
readline.set_completer(completey)
y_inp = raw_input('Enter y-value to extract: ')

# Get output file extension
out_ext = raw_input('Enter output files extension: ')

# Post-processing
x_str = x_inp.replace('-',' ')
y_str = y_inp.replace('-',' ')
y_str = 'ZZZ ' + y_str

# Get a list of output file
file_list = glob.glob('*.'+out_ext)

# Create list to store these values
x_val = []
y_val = []

# Iterate through file list
for file in file_list:
    # Open and read files
    ifile = open(file,'r')
    reader = ifile.readlines()
    print("Processing the file {}".format(file))

    # Go through each row
    for row in reader:
        # Achieve the x value we want
        if x_str in row:
            row_list =  row.split(':')
            x_val.append(float(row_list[1].strip().replace('\n','')))

        # Find row with the timing we want
        # In the ZZZ timing, wall avg and wall total the same...
        if y_str in row:
            row_split = row.split('|')
            title = row_split[0].strip()
            try:
                raw_values = row_split[1].replace('\n','').strip().replace('  ',' ')
                y_val.append(float(raw_values.split()[1]))
            except:
                pass

# Now sort the timing in increasing number of cores
y_val_sorted = [y for (x,y) in sorted(zip(x_val,y_val))]
x_val.sort()

# Save to a CSV file
print("Processing of files completed !!!")
print("Saving to csv files...")

# Save results to output file
out_file = x_inp+'-'+y_inp+'.csv'
with open(out_file, 'wb') as f:
    writer = csv.writer(f)
    writer.writerow([x_inp, y_inp])
    writer.writerows(izip(x_val, y_val_sorted))

print("Saving to csv files complete!")
