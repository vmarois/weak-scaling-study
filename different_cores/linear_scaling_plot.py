# This script outputs 3 plots as pdf: 
# 'dofs_plot.pdf' showing the nb of degrees of freedom per core & in total in fct of the nb of proc,
# 'steps_timings_plot.pdf' showing the different steps timings in fct of the nb of proc,
# 'weak_scaling_efficiency_plot.pdf' showing the efficiency of the benchmark.

from __future__ import print_function
import os

import numpy as np 
import seaborn as sns
import matplotlib.pyplot as plt

import xmltodict
import pandas as pd


def convert_table_to_dataframe(filename):
    """Converts filename (.xml) into a Pandas DataFrame."""
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
    """ Concatenates a list of numbers into a string, with ',' as separator."""
    string = ""
    for i, core in enumerate(cores_combination):
        string += str(core)
        if not i == len(cores_combination) - 1:
            string += ","
    return string


def add_value_to_plot(ax):
    """ Add the value above the bars."""
    for p in ax.patches:
        height = p.get_height()
        ax.text(p.get_x()+p.get_width()/2., 1.05*height, '%1.2f' % float(height), ha='center', va='bottom')


# Create directory to store pdf files.
directory = os.path.join(os.getcwd(), 'output/pdf')
if not os.path.exists(directory):
    os.mkdir(directory)

# CPU combinations to be studied.
cores_combinations = [ [0,4], [0,1,4,5], [0,1,2,4,5,6], range(0,8)]
labels = ['1 + 1', '2 + 2', '3 + 3', 'All 8 cores']

# Define the number of processes to run & the steps to extract from the workload.
cores_number = [len(x) for x in cores_combinations]
steps = ['Assemble', 'FunctionSpace', 'Solve', 'Total']

# Define lists & array to plot the different steps timings in function of the number of processes.
cores = [None] * (len(cores_combinations) * len(steps))
stages = [None] * (len(cores_combinations) * len(steps))
timings = np.zeros(len(cores_combinations) * len(steps))

# Define arrays to plot the efficiency of the weak-scaling benchmark.
temp_perc = np.zeros(len(cores_combinations))
perc = np.zeros(len(cores_combinations))

# Define lists & arrays to store the number of dofs per core.
ndofsprocesses = np.zeros(2 * len(cores_combinations))
ndofslabel = [None] * (2 * len(cores_combinations))
ndofs = np.zeros(2 * len(cores_combinations))
ndoftypes = ['Per core', 'Total']


# Extracting results from the xml files, and storing them in the appropriate variables.
for i, label in enumerate(labels):

    # Outputs data from xml files
    raw_timings = convert_table_to_dataframe("output/timings/timings_{}.xml".format(cores_to_str(cores_combinations[i])))
    raw_ndofs = convert_table_to_dataframe("output/dofs/dofs_{}.xml".format(cores_to_str(cores_combinations[i])))

    # Structure the lists & arrays for the DataFrame (ndofs plot)
    for k, ndoftype in enumerate(ndoftypes):
        ndofs[i * len(ndoftypes) + k] = raw_ndofs.loc["ndofs"]["{}".format(ndoftype)]
        ndofslabel[i * len(ndoftypes) + k] = ndoftype
        ndofsprocesses[i * len(ndoftypes) + k] = len(cores_combinations[i])

    for j, step in enumerate(steps):
        # Order the labels and timings for a proper grouped barplot (timings plot).
        cores[i*len(steps) + j] = label
        stages[i*len(steps) + j] = step
        timings[i*len(steps) + j] = raw_timings.loc["wall tot"]["ZZZ {}".format(step)]
        
        # Sum the timings of the steps and store them in temp_perc.
	# Not taking in the 'Total' timing as not needed for the efficiency plot.
        if not step == 'Total':
            temp_perc[i] += raw_timings.loc["wall tot"]["ZZZ {}".format(step)]

    # For the efficiency plot, compute the percentages as defined.
    perc[i] = (temp_perc[0]/temp_perc[i]) * 100

print("Results have been extracted.")


# Define DataFrame object for the ndofs & total per core plot.
df0 = pd.DataFrame({'Processes': ndofsprocesses, 'Type': ndofslabel, 'Ndofs': ndofs}, columns = ['Processes', 'Type', 'Ndofs'])
print("DataFrame object (dofs) has been created.")

# Define DataFrame object for the different steps timings plot.
df1 = pd.DataFrame({'Cores': cores, 'Stages': stages, 'Timing': timings}, columns = ['Cores', 'Stages', 'Timing'])
print("DataFrame object (steps timings) has been created.")

# Define DataFrame object for the efficiency plot.
df2 = pd.DataFrame({'Processes': cores_number, 'Percentages': perc}, columns = ['Processes', 'Percentages'])
print("DataFrame object (efficiency) has been created.")


sns.set_context("paper")
colors = sns.color_palette("muted")

# Plot the ndofs total & per core.
ax0 = sns.barplot(x='Processes', y='Ndofs', hue='Type', data=df0)
ax0.set_title('Evolution of ndofs with the number of processes.')
#  Layout & save plot.
plt.xlabel(r"Number of processes")
plt.ylabel(r"Number of degrees of freedom")
plt.savefig("output/pdf/dofs_plot.pdf", bbox_inches='tight')
print("Done, 'dofs_plot' saved to pdf.")
#  Clear matplotlib.pyplot.
plt.clf()


# Plot the different steps timings.
ax1 = sns.barplot(x='Cores', y='Timing', hue='Stages', data=df1, palette=colors)
ax1.set_title('Linear Scaling Verification')
add_value_to_plot(ax1)
#  Layout & save plot.
plt.xlabel(r"Number of processes")
plt.ylabel(r"Wall time (s)")
plt.savefig("output/pdf/steps_timings_plot.pdf", bbox_inches='tight')
print("Done, 'steps_timings_plot' saved to pdf.")
#  Clear matplotlib.pyplot.
plt.clf()


# Plot the efficiency.
sns.set()
ax2 = sns.regplot(x='Processes', y='Percentages', data=df2)
ax2.set_title('Weak Scaling Efficiency Plot\non odroid')
#  Layout & save plot.
plt.xlabel(r"Number of processes")
plt.ylabel(r"Efficiency (%)")
plt.savefig("output/pdf/weak_scaling_efficiency_plot.pdf", bbox_inches='tight')
print("Done, 'weak_scaling_efficiency_plot' has been saved to pdf.")
