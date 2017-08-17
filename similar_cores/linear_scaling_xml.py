# This script runs several times demo_poisson, with an increasing number
# of parallel processes each time. The results (timings and otherwise)
# are saved to files for future plotting.

import os


def cores_to_str(cores_combination):
    """ Concatenates a list of numbers into a string, with ',' as separator."""
    string = ""
    for i, core in enumerate(cores_combination):
        string += str(core)
        if not i == len(cores_combination) - 1:
            string += ","
    return string


# CPU combinations to be studied.
cores_combinations = [ range(0, 1), range(0, 2), range(0, 3), range(0, 4), range(0, 5), range(0, 6), range(0, 7), range(0, 8)]
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


#Generate the appropriate command for the weak-scaling test and then run it.
#The number of dofs is constant and fixed to 120000 (maximum value without crashing).
for i in range(len(cores_combinations)):
    
    filename = os.path.join(os.getcwd(), 'output/timings/timings_{}'.format(cores_to_str(cores_combinations[i])))
    # Check if the corresponding xmlfile already exists, and if yes skip the command.
    
    if not os.path.isfile(filename):
        command = "mpiexec -n " + str(cores_number[i]) + " -bind-to user:" + cores_to_str(cores_combinations[i]) + " weak-scaling-demo/build/demo_poisson --ndofs=120000 --xmlname=" + cores_to_str(cores_combinations[i])
        os.system(command)  # Run demo_poisson with mpiexec.
    else:
        print("There is already a file named timings_{}".format(cores_to_str(cores_combinations[i])) + ".xml. Skipping the corresponding command.")

