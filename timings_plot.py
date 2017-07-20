#This script can bu used to plot various results 
#From the weak-scaling study.
from __future__ import print_function
import os

path = os.getcwd() + "/weak-scaling-demo"
os.chdir(path)
os.system("mkdir xmlfiles")

#CPU combinations to be studied.
cores_combinations = ["0,1,2,3,4,5,6,7", "0,1,2,3", "4,5,6,7", "0,4", "0,1,4,5", "0,1,2,4,5,6"]
cores_number = [8, 4, 4, 2, 4, 6]

#Generate the appropriate command for the weak-scaling test and then run it.
#The number of dofs is constant and fixed to 124 250 (maximum value without crashing).
for i in range(0, len(cores_combinations)):
	command = "mpiexec -n " + cores_number[i] + " -bind-to user:" + cores_combinations[i] + " ./demo_poisson --ndofs=124250 --xmlname=" + cores_combinations[i]
	os.system(command)
