# This script outputs the different steps timings & the total one
# in function of the different core combinations used.

from __future__ import print_function
import os

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import xmltodict
import pandas as pd

def file_to_float(filename):
    '''Reads in a .txt file and converts the output into float.'''
    with open(filename, 'r') as f:
        str = f.read()
        f.close()
        str = str[1:]
        str = str[:-1]
        str = str.split(',')
        flt = list(map(float, str))
        return flt

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

def cores_to_str(cores_combination):
    string = ""
    for i, core in enumerate(cores_combination):
        string += str(core)
        if not i == len(cores_combination) - 1:
            string += ","

    return string

def add_value_to_plot(ax):
    ''' Add the value above the bars.'''
    for p in ax.patches:
        height = p.get_height()
        ax.text(p.get_x()+p.get_width()/2., 1.05*height, '%1.2f' % float(height), ha='center', va='bottom')


# Create directory to store pdf files.
directory = os.path.join(os.getcwd(), 'output/pdf')
if not os.path.exists(directory):
    os.mkdir(directory)

# CPU combinations to be studied.
cores_combinations = [ range(0, 8), range(0, 4), range(4, 8), [0,4], [0,1,4,5], [0,1,2,4,5,6]]
cores_number = [len(x) for x in cores_combinations]

# Define lists used for the timings plot.
labels = ['8 cores', '4 smalls', '4 bigs', '1 + 1', '2 + 2', '3 + 3']
steps = ['Assemble', 'FunctionSpace', 'Solve', 'Total']
cores = [None] * (len(cores_combinations) * len(steps))
stages = [None] * (len(cores_combinations) * len(steps))
values = np.zeros(len(cores_combinations) * len(steps))

# Define lists for the energy consumption plot.
wh_steps = ['Watthour consumed ','Average current drawn (A) ']
wh_cores = [None] * (len(cores_combinations) * len(wh_steps))
wh_stages = [None] * (len(cores_combinations) * len(wh_steps))
wh_values = np.zeros(len(cores_combinations) * len(wh_steps))
wh_timings = np.zeros(len(cores_combinations))

# Extracting results from the xml files.
print('Extracting result from the xml files...')
for i, label in enumerate(labels):
    timings = convert_table_to_dataframe("output/timings/timings_{}.xml".format(cores_to_str(cores_combinations[i])))
    wh_timings[i] = timings.loc["wall tot"]["ZZZ Total"]

    for j, step in enumerate(steps):
        cores[i*len(steps) + j] = label
        stages[i*len(steps) + j] = step
        values[i*len(steps) + j] = timings.loc["wall tot"]["ZZZ {}".format(step)]

# Extracting the watthour measures from file.
print('Extracting the watthour measures from file...')
wh = file_to_float('output/wh_measures.txt')


for n, wh_label in enumerate(labels):
    for k, wh_step in enumerate(wh_steps):
        wh_cores[n*len(wh_steps) + k] = wh_label
        wh_stages[n*len(wh_steps) + k] = wh_step
        if k == 0:
            wh_values[n*len(wh_steps) + k] = wh[n]
        else:
            wh_values[n*len(wh_steps) + k] = (wh[n] * 3600)/(wh_timings[n] * 5.25)

print("Results have been extracted.")

# Define DataFrame object.
dft = pd.DataFrame({'Cores': cores, 'Stages': stages, 'Timing': values}, columns = ['Cores', 'Stages', 'Timing'])
print("DataFrame object (timings)  has been created.")
dfwh = pd.DataFrame({'Cores': wh_cores, 'Measures': wh_stages, 'Values': wh_values}, columns = ['Cores', 'Measures', 'Values'])
print("DataFrame object (energy consumption) has been created.")

# Plot 'total_&_stages_timings'
sns.set_context("paper")
colors = sns.color_palette("muted")
ax = sns.barplot(x='Cores', y='Timing', hue='Stages', data=dft, palette=colors)
ax.set_title('Total & Stages Timings')
add_value_to_plot(ax)
plt.xlabel(r"Core combinations")
plt.ylabel(r"Wall time (s)")
plt.savefig("output/pdf/total_&_stages_timings.pdf", bbox_inches='tight')
print("Done, 'total_&_stages_timings' has been saved to pdf.")

# Plot 'energy_consumption'.
plt.clf()
ax = sns.barplot(x='Cores', y='Values', hue='Measures', data=dfwh, palette=colors)
ax.set_title('Energy consumption of various core combinations')
add_value_to_plot(ax)
plt.xlabel(r"Core combinations")
plt.ylabel(r"Measures")
plt.savefig("output/pdf/energy_consumption.pdf", bbox_inches='tight')
print("Done, 'energy_consumption' has been saved to pdf.")
