#This script can bu used to plot various results 
#From the weak-scaling study.
from __future__ import print_function
import os

import numpy as np 

import xmltodict
import pandas as pd

def convert_table_to_dataframe(filename):
    with open(filename) as f:
        d = xmltodict.parse(f)

    d = d["dolfin"]["table"]["row"]

    d_new = {}

    for row in d:
        operation = row["@key"]
        d_new[operation] = {}
        for col in row["col"]:
            key = col["@key"]
            value = col["@value"]
            if key == "reps":
                d_new[operation][key] = int(value)
            else:
                d_new[operation][key] = float(value)


    df = pd.DataFrame(d_new)

    return df

directory = os.path.join(os.getcwd(), 'weak-scaling-demo', 'xmlfiles')
if not os.path.exists(directory):
    os.mkdir(directory)

#CPU combinations to be studied.
cores_combinations = ["0,1,2,3,4,5,6,7", "0,1,2,3", "4,5,6,7", "0,4", "0,1,4,5", "0,1,2,4,5,6"]
cores_number = ["8", "4", "4", "2", "4", "6"]

#Generate the appropriate command for the weak-scaling test and then run it.
#The number of dofs is constant and fixed to 124 250 (maximum value without crashing).
for i in range(len(cores_combinations)):
	command = "mpiexec -n " + cores_number[i] + " -bind-to user:" + cores_combinations[i] + " weak-scaling-demo/build/demo_poisson --ndofs=120000 --xmlname=" + cores_combinations[i]
	os.system(command)

#Extracting results from the xml files.
for i in range(0, len(cores_combinations)):
        timings = convert_table_to_dataframe("weak-scaling-demo/xmlfiles/timings_{}.xml".format(cores_combinations[i]))
        func_spaces_times = np.zeros_like(timings)
        for j, timing in enumerate(timings):
                func_spaces_times[j] = timing.loc['wall tot']['ZZZ FunctionSpace']

        print(func_spaces_times)

#Extract FunctionSpace timings.
func_spaces_times = np.zeros_like(timings)
for i, timings in enumerate(timings):
    func_spaces_times[i] = float(timings.loc['wall tot']['ZZZ FunctionSpace'])

#Extract Assemble timings.
assemble_times = np.zeros_like(timings)
for i, timings in enumerate(timings):
    assemble_times[i] = float(timings.loc['wall tot']['ZZZ Assemble'])

#Extract Solve timings.
solve_times = np.zeros_like(timings)
for i, timings in enumerate(timings):
    solve_times[i] = float(timings.loc['wall tot']['ZZZ Solve'])

#Extract Total timings.
total_times = np.zeros_like(timings)
for i, timings in enumerate(timings):
    total_times[i] = float(timings.loc['wall tot']['ZZZ Total'])
