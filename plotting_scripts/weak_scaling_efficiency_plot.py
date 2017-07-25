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

# Create directory to store pdf files.
directory = os.path.join(os.getcwd(), 'pdf')
if not os.path.exists(directory):
    os.mkdir(directory)

# CPU combinations to be studied.
cores_combinations = [[0,4], [0,1,4,5], [0,1,2,4,5,6], range(0,8)]
cores_number = [len(x) for x in cores_combinations]

def cores_to_str(cores_combination):
    string = ""
    for i, core in enumerate(cores_combination):
        string += str(core)
        if not i == len(cores_combination) - 1:
            string += ","

    return string

# Define lists used for data management.
processes = [2, 4, 6, 8]
steps = ['Assemble', 'FunctionSpace', 'Solve']
tempvalues = np.zeros(len(cores_combinations))
values = np.zeros(len(cores_combinations))

# Extracting results from the xml files.
for i, proc in enumerate(processes):
    timings = convert_table_to_dataframe("xmlfiles/timings_{}.xml".format(cores_to_str(cores_combinations[i])))
    for j, step in enumerate(steps):
        tempvalues[i] += timings.loc["wall tot"]["ZZZ {}".format(step)]

    values[i] = tempvalues[0]/tempvalues[i]
    values[i] *= 100

print("Results have been extracted.")

# Define DataFrame object.
df = pd.DataFrame({'Processes': processes, 'Percentages': values}, columns = ['Processes', 'Percentages'])
print("DataFrame object has been created.")
print(df)

#sns.set_context("paper")
sns.set()
ax = sns.regplot(x='Processes', y='Percentages', data=df)
ax.set_title('Weak Scaling Efficiency Plot\n'
     'on odroid')

# Layout & save plot.
plt.xlabel(r"Number of processes")
plt.ylabel(r"Efficiency (%)")
plt.savefig("pdf/weak_scaling_efficiency.pdf", bbox_inches='tight')
print("Done, plot has been saved to pdf.")
