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



def add_value_to_plot(ax):
    """ Add the value above the bars."""
    for p in ax.patches:
        height = p.get_height()
        ax.text(p.get_x()+p.get_width()/2., 1.05*height, '%1.2f' % float(height), ha='center', va='bottom')


# Create directory to store pdf files.
directory = os.path.join(os.getcwd(), 'output/pdf')
if not os.path.exists(directory):
    os.mkdir(directory)

# Define some lists used for the timings plot.
steps = ['Assemble', 'FunctionSpace', 'Solve', 'Output','Total']
values = np.zeros(len(steps))

# Extracting results from the xml files.
print('Extracting result from the xml files...')

timings = convert_table_to_dataframe("output/timings/timings_wgts_distributed.xml")

for j, step in enumerate(steps):
        values[j] = timings.loc["wall tot"]["ZZZ {}".format(step)]

print("Results have been extracted.")

# Define DataFrame objects.
df = pd.DataFrame({'Steps': steps, 'Timing': values}, columns = ['Steps', 'Timing'])
print("DataFrame object (timings)  has been created.")

sns.set_context("paper")
colors = sns.color_palette("muted")

# Plot 'total_&_stages_timings'
ax = sns.barplot(x='Steps', y='Timing', data=df, palette=colors)
ax.set_title('Stages Timings (8 cores with 0.45 weight dist.')
add_value_to_plot(ax)
plt.xlabel(r"Stages")
plt.ylabel(r"Wall time (s)")
plt.savefig("output/pdf/stages_timings_wgts_0_45.pdf", bbox_inches='tight')
print("Done, 'stages_timings_wgts_0.4' has been saved to pdf.")
