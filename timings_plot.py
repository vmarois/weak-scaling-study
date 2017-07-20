#This script can bu used to plot various results 
#From the weak-scaling study.
from __future__ import print_function
import os

import numpy as np 

import xmltodict
import pandas as pd

def convert_table_to_dataframe(filename):
    with open(filename, "rb") as f:
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

print(cores_combination_to_str(cores_combinations[0]))

function_spaces = np.zeros(len(cores_combinations))

# Extracting results from the xml files.
for i in range(0, len(cores_combinations)):
    timings = convert_table_to_dataframe("xmlfiles/timings_{}.xml".format(cores_to_str(cores_combinations[i])))
    function_spaces[i] = timings.loc["wall tot"]["ZZZ Total"]

print(function_spaces)
