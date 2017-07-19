#This script can bu used to plot various results 
#From the weak-scaling study.
from __future__ import print_function
from subprocess import call

import numpy as np 
import seaborn as sns
import matplotlib.pyplot as plt

import xmltodict
import pandas as pd

sns.set_style("ticks")

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

#CPU combinations to be studied.
cores_combinations = ["0,1,2,3,4,5,6,7", "0,1,2,3", "4,5,6,7", "0,4", "0,1,4,5", "0,1,2,4,5,6"]
cores_number = [8, 4, 4, 2, 4, 6]

#Generate the appropriate command for the weak-scaling test and then run it.
#The number of dofs is constant and fixed to 124 250 (maximum value without crashing).

command = "mpiexec -n " + cores_number[0] + " -bind-to user:" + cores_combinations[0] + " ./demo_poisson --ndofs=124250 --xmlname=" + cores_combinations[0]
call(["echo", command])

#Extracting results from the xml files.
timings = [convert_table_to_dataframe("output/study_one/timings_{}.xml".format(i)) for i in range(0, len(cores_combinations))]

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


#NOT MODIFIED UNDER THIS LINE YET
#-------------------------------------------------

sns.set_context("paper")
colors = sns.color_palette("muted")

fig = plt.figure(figsize=(3, 2.2))
ax1 = plt.gca()
plt.grid(False)
plt.xscale('log')
ax1.set_xlim(10**-5, 10**-1)
plt.plot(tolerances, times, "-", marker="o", label="time RAPOD", color=colors[0])
plt.xlabel(r"integration tolerance")
plt.ylabel(r"wall time (s)")

pod_timings = convert_table_to_dataframe("output/study_one/pod.xml")
time = float(pod_timings.loc['wall tot']['Total'])
pod_times = np.ones_like(tolerances)
pod_times *= pod_time
plt.plot(tolerances, pod_times, "--", marker=None, color=colors[0], label="time POD")
lgd1 = plt.legend(frameon=False, handlelength=4, bbox_to_anchor=(-0.2, 0.9))

results = pd.read_json("output/study_one/results.json").T
ax2 = ax1.twinx()
ax2.set_yscale('log')
ax2.set_ylim(10**-2, 1.0)
ax2.plot(results.drop('pod')["tolerance"], results.drop('pod')["error"], marker="s", color=colors[2], label="error RAPOD")
plt.grid(False)
plt.xscale('log')
pod_errors = np.ones_like(tolerances)
pod_errors *= results.loc['pod']['error']
ax2.plot(tolerances, pod_errors, "--", marker=None, color=colors[2], label="error POD")
ax2.set_ylabel(r"$||e||_{H^1}$")

lgd2 = plt.legend(frameon=False, handlelength=4, bbox_to_anchor=(1.8, 0.9))
plt.savefig("output/study_one/plot.pdf", bbox_extra_artists=(lgd1,lgd2), bbox_inches='tight')

# Time performance plot

for i, rapod_timing in enumerate(rapod_timings):
    rapod_timing['tolerance'] = tolerances[i]
    rapod_timing['method'] = "RAPOD"

fem_timings = convert_table_to_dataframe("output/study_one/fem.xml") 
fem_timings['method'] = "FEM"

pod_timings['tolerance'] = "N/A" 
pod_timings['method'] = "POD"
rapod_timings.append(pod_timings)
rapod_timings.append(fem_timings)
df = pd.concat(rapod_timings)
df["tolerance"] = df["tolerance"].fillna("N/A")
df.index.name = "timing"
df.set_index(["method", "tolerance"], append=True, inplace=True)
df = df.reorder_levels(["method", "tolerance", "timing"])
df["Projections"] = df["FE Vector to POD Vector"] + df["FE Matrix to POD Matrix"] + df["POD Vector to FE Vector"]
df["Linear algebra"] = (df['Dense Cholesky Solve'] + df['Dense Cholesky Factor']).apply(lambda x: x if not pd.isnull(x) else x)
df.loc[("FEM", "N/A"), "Linear algebra"] = df.loc[("FEM", "N/A"), "PETSc Krylov solver"].values
print(df.loc[("FEM", "N/A"), "PETSc Krylov solver"])
print(df)

df = df.rename(columns={"Assemble system": "Assemble matrix", "Assemble cells": "Assemble RHS"})
interesting_cols = ["Projections", "Assemble RHS", "Linear algebra", "Total"]
performance = df[df.index.get_level_values(2) == "wall tot"][interesting_cols] 

sns.set_context('talk')
fig = plt.figure(figsize=(3, 2.2))
ax = performance.plot.barh()
plt.xscale('log')
plt.xlabel('wall time (s), log scale')
plt.savefig("output/study_one/rapod_log.pdf", bbox_inches='tight')

fig = plt.figure(figsize=(3, 2.2))
ax = performance.plot.barh()
plt.xlabel('wall time (s), linear scale')
plt.legend(loc='lower right')
plt.savefig("output/study_one/rapod_linear.pdf", bbox_inches='tight')
