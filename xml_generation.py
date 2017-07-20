#This script runs a series of weak-scaling
#tests to generate xml files for future plotting.
from __future__ import print_function
import os

# CPU combinations to be studied.
cores_combinations = [ range(0, 8), range(0, 4), range(4, 8), [0,4], [0,1,4,5], [0,1,2,4,5,6]]
cores_number = [len(x) for x in cores_combinations]

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
	command = "mpiexec -n " + cores_number[i] + " -bind-to user:" + cores_to_str(cores_combinations[i]) + " weak-scaling-demo/build/demo_poisson --ndofs=120000 --xmlname=" + cores_combinations[i]
	os.system(command)

