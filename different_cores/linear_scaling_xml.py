# This script runs a series of weak-scaling
# tests and outputs the results to xml files.

import os

# CPU combinations to be studied.
cores_combinations = [ [0,4], [0,1,4,5], [0,1,2,4,5,6], range(0,8)]
cores_number = [len(x) for x in cores_combinations]

# Create directory to store generated xml files.
directory = os.path.join(os.getcwd(), 'xmlfiles')
if not os.path.exists(directory):
    os.mkdir(directory)

# Create directory to store outputs files (*pvd, *.pvtu *.xdmf, *.vtu)
directory = os.path.join(os.getcwd(), 'output')
if not os.path.exists(directory):
    os.mkdir(directory)

def cores_to_str(cores_combination):
    string = ""
    for i, core in enumerate(cores_combination):
        string += str(core)
        if not i == len(cores_combination) - 1:
            string += ","

    return string

#Generate the appropriate command for the weak-scaling test and then run it.
#The number of dofs is constant and fixed to 120000 (maximum value without crashing).
for i in range(len(cores_combinations)):
    filename = os.path.join(os.getcwd(), 'xmlfiles', 'timings_{}'.format(cores_to_str(cores_combinations[i])))
    # Check if the corresponding xmlfile already exists, and if yes skip the command.
    if not os.path.isfile(filename):
        command = "mpiexec -n " + str(cores_number[i]) + " -bind-to user:" + cores_to_str(cores_combinations[i]) + " weak-scaling-demo/build/demo_poisson --ndofs=120000 --xmlname=" + cores_to_str(cores_combinations[i])
        os.system(command)
    else:
        print("There is already a file named timings_{}".format(cores_to_str(cores_combinations[i])) + ".xml. Skipping the corresponding command.")

