# This script runs several times demo_poisson with parallel processing, varying
# each time the core combinations to use. The timings and number of degrees of freedom,
# alongside the watthour consumed for each combination are saved to files for future plotting.

import os
import subprocess


def cores_to_str(cores_combination):
    """ Concatenates a list of numbers into a string, with ',' as separator."""
    string = ""
    for i, core in enumerate(cores_combination):
        string += str(core)
        if not i == len(cores_combination) - 1:
            string += ","
    return string

# CPU combinations to be studied.
cores_combinations = [ range(0, 8), range(0, 4), range(4, 8), [0,4], [0,1,4,5], [0,1,2,4,5,6]]
cores_number = [len(x) for x in cores_combinations]

# Create directory to store generated files.
directory = os.path.join(os.getcwd(), 'output')
if not os.path.exists(directory):
    os.mkdir(directory)

# Create directory to store generated timings xml files.
directory = os.path.join(os.getcwd(), 'output/timings')
if not os.path.exists(directory):
    os.mkdir(directory)

# Create directory to store generated ndofs xml files.
directory = os.path.join(os.getcwd(), 'output/dofs')
if not os.path.exists(directory):
    os.mkdir(directory)

# Create directory to store other outputs files (*pvd, *.pvtu *.xdmf, *.vtu)
directory = os.path.join(os.getcwd(), 'output/others')
if not os.path.exists(directory):
    os.mkdir(directory)

# Define empty list to store the watthour measures.
wh =[]

# Generate the appropriate command for the weak-scaling test and then run it.
# The number of dofs is constant and fixed to 120000 (maximum value without crashing).
for i in range(len(cores_combinations)):
    filename = os.path.join(os.getcwd(), 'output/timings/timings_{}'.format(cores_to_str(cores_combinations[i])))

    # Check if the corresponding .xml file already exists, and if yes skip the command.
    if not os.path.isfile(filename):
        
        # Construct the commands to pass to os.system()
        init_meter = "sudo odroid-smartpower-linux/init"
        generate_xml = "mpiexec -n " + str(cores_number[i]) + " -bind-to user:" + cores_to_str(cores_combinations[i]) + " weak-scaling-demo/build/demo_poisson --ndofs=120000 --xmlname=" + cores_to_str(cores_combinations[i])
        get_watthour = "sudo odroid-smartpower-linux/watthour"
        
        # Run the commands
        os.system(init_meter)  # Reinitializes the wattmeter and starts the watthour measures.
        os.system(generate_xml)  # Run demo_poisson with mpiexec and the specific core combinations.
        wh.append(float(subprocess.getoutput(get_watthour)))  # Get the current watthour measure, and store it to wh.
        
    else:
        print("There is already a file named timings_{}".format(cores_to_str(cores_combinations[i])) + ".xml. Skipping the corresponding command.")

# Save watthour measures to a file for future plotting.
f = open("output/wh_measures.txt", "w")
f.write(str(wh))
f.close()
