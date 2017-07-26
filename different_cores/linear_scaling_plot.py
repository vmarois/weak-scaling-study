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

def cores_to_str(cores_combination):
    string = ""
    for i, core in enumerate(cores_combination):
        string += str(core)
        if not i == len(cores_combination) - 1:
            string += ","

    return string

# Create directory to store pdf files.
directory = os.path.join(os.getcwd(), 'pdf')
if not os.path.exists(directory):
    os.mkdir(directory)

# CPU combinations to be studied.
cores_combinations = [ [0,4], [0,1,4,5], [0,1,2,4,5,6], range(0,8)]
cores_number = [len(x) for x in cores_combinations]

# Define the range of processes covered & the steps to extract from the workload.
processes = ['1 + 1', '2 + 2', '3 + 3', 'All 8 cores']
steps = ['Assemble', 'FunctionSpace', 'Solve', 'Total']

# Define variables to plot the different steps timings in function of the number of processes.
cores = [None] * (len(cores_combinations) * len(steps))
stages = [None] * (len(cores_combinations) * len(steps))
timings = np.zeros(len(cores_combinations) * len(steps))

# Define variables to plot the efficiency of the weak-scaling benchmark.
temp_perc = np.zeros(len(cores_combinations))
perc = np.zeros(len(cores_combinations))

# Extracting results from the xml files, and storing them in the appropriate variables.
for i, proc in enumerate(processes):
    raw_timings = convert_table_to_dataframe("xmlfiles/timings_{}.xml".format(cores_to_str(cores_combinations[i])))
    for j, step in enumerate(steps):
        cores[i*len(steps) + j] = proc
        stages[i*len(steps) + j] = step
        timings[i*len(steps) + j] = raw_timings.loc["wall tot"]["ZZZ {}".format(step)]
        # Sum the timings of the steps and store them in temp_perc.
	# Not taking in the 'Total' timing as not needed for the efficiency plot.
        if not step == 'Total':
            temp_perc[i] += raw_timings.loc["wall tot"]["ZZZ {}".format(step)]

    # For the efficiency plot, compute the percentages as defined.
    perc[i] = (temp_perc[0]/temp_perc[i]) * 100

print("Results have been extracted.")

# Define DataFrame object for the different steps timings plot.
df1 = pd.DataFrame({'Cores': cores, 'Stages': stages, 'Timing': timings}, columns = ['Cores', 'Stages', 'Timing'])
print("DataFrame object (steps timings) has been created.")

# Define DataFrame object for the efficiency plot.
df2 = pd.DataFrame({'Processes': cores_number, 'Percentages': perc}, columns = ['Processes', 'Percentages'])
print("DataFrame object (efficiency) has been created.")

# Plot the different steps timings.
sns.set_context("paper")
colors = sns.color_palette("muted")
ax1 = sns.barplot(x='Cores', y='Timing', hue='Stages', data=df1, palette=colors)
ax1.set_title('Linear Scaling Verification')
#Add timing values above bars in plot.
for p in ax1.patches:
    height = p.get_height()
    ax1.text(p.get_x()+p.get_width()/2., 1.05*height,
                "%.1f" % round(height,1),
                ha='center', va='bottom') 
#Layout & save plot.
plt.xlabel(r"Number of processes")
plt.ylabel(r"Wall time (s)")
plt.savefig("pdf/steps_timings_plot.pdf", bbox_inches='tight')
print("Done, 'steps_timings_plot' saved to pdf.")
#Clear matplotlib.pyplot.
plt.clf()

# Plot the efficiency.
sns.set()
ax2 = sns.regplot(x='Processes', y='Percentages', data=df2)
ax2.set_title('Weak Scaling Efficiency Plot\n'
     'on odroid')
#Layout & save plot.
plt.xlabel(r"Number of processes")
plt.ylabel(r"Efficiency (%)")
plt.savefig("pdf/weak_scaling_efficiency_plot.pdf", bbox_inches='tight')
print("Done, 'weak_scaling_efficiency_plot' has been saved to pdf.")
