#This script runs a series of weak-scaling
#tests to generate xml files for future plotting.
from __future__ import print_function
import os

#CPU combinations to be studied.
cores_combinations = ["0,1,2,3,4,5,6,7", "0,1,2,3", "4,5,6,7", "0,4", "0,1,4,5", "0,1,2,4,5,6"]
cores_number = ["8", "4", "4", "2", "4", "6"]

#Generate the appropriate command for the weak-scaling test and then run it.
#The number of dofs is constant and fixed to 120000 (maximum value without crashing).
for i in range(len(cores_combinations)):
	command = "mpiexec -n " + cores_number[i] + " -bind-to user:" + cores_combinations[i] + " weak-scaling-demo/build/demo_poisson --ndofs=120000 --xmlname=" + cores_combinations[i]
	os.system(command)

