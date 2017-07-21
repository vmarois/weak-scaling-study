# This script can be used to plot various results 
# From the weak-scaling study.

from __future__ import print_function
import os

import numpy as np 
import seaborn as sns
import matplotlib.pyplot as plt

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

# Define lists to store results.
assemble = np.zeros(len(cores_combinations))
function_space = np.zeros(len(cores_combinations))
solve = np.zeros(len(cores_combinations))
total = np.zeros(len(cores_combinations))

# Extracting results from the xml files.
for i in range(0, len(cores_combinations)):
    timings = convert_table_to_dataframe("xmlfiles/timings_{}.xml".format(cores_to_str(cores_combinations[i])))
    assemble[i] = timings.loc["wall tot"]["ZZZ Assemble"]
    function_space[i] = timings.loc["wall tot"]["ZZZ FunctionSpace"]
    solve[i] = timings.loc["wall tot"]["ZZZ Solve"]
    total[i] = timings.loc["wall tot"]["ZZZ Total"]

# Print some results.
print("FunctionSpace timings : ")
print(function_spaces)

print("Assemble timings : ")
print(assemble)

print("Solve timings : ")
print(solve)

print("Total timings : ")
print(total)

print("Generating the plots...")
sns.set_context("paper")
colors = sns.color_palette("muted")

cores = ['8 cores', '4 smalls', '4 bigs', '1 + 1', '2 + 2', '3 + 3']
fig, ax  = plt.subplots(figsize=(3, 2.2))
sns.barplot(function_spaces,cores) 
plt.xlabel(r"wall time (s)")
plt.ylabel(r"cores combination")
plt.savefig("total_times.pdf", bbox_inches='tight')
print("Done. Results have been outputted to PDF.")
