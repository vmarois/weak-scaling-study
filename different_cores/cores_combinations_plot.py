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
directory = os.path.join(os.getcwd(), 'output/pdf')
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

# Define lists used for data management.
labels = ['8 cores', '4 smalls', '4 bigs', '1 + 1', '2 + 2', '3 + 3']
steps = ['Assemble', 'FunctionSpace', 'Solve', 'Total']
cores = [None] * (len(cores_combinations) * len(steps))
stages = [None] * (len(cores_combinations) * len(steps))
values = np.zeros(len(cores_combinations) * len(steps))

# Extracting results from the xml files.
for i, label in enumerate(labels):
    timings = convert_table_to_dataframe("output/timings/timings_{}.xml".format(cores_to_str(cores_combinations[i])))
    for j, step in enumerate(steps):
        cores[i*len(steps) + j] = label
        stages[i*len(steps) + j] = step
        values[i*len(steps) + j] = timings.loc["wall tot"]["ZZZ {}".format(step)]

print("Results have been extracted.")

# Define DataFrame object.
df = pd.DataFrame({'Cores': cores, 'Stages': stages, 'Timing': values}, columns = ['Cores', 'Stages', 'Timing'])
print("DataFrame object has been created.")

sns.set_context("paper")
colors = sns.color_palette("muted")
ax = sns.barplot(x='Cores', y='Timing', hue='Stages', data=df, palette=colors)
ax.set_title('Total & Stages Timings')

# Add timing values above bars in plot.
for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x()+p.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom') 

# Layout & save plot.
plt.xlabel(r"Core combinations")
plt.ylabel(r"Wall time (s)")
plt.savefig("output/pdf/total_&_stages_timings.pdf", bbox_inches='tight')
print("Done, 'total_&_stages_timings' has been saved to pdf.")
