# First test to determine if there's a significant difference in performance between a small core
# and a big core. Focus first on the time taken to run demo_poisson with ndofs = 1 000 000, the
# wh consumed.

import os
import subprocess

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

# Create directory to store generated files.
directory = os.path.join(os.getcwd(), 'output')
if not os.path.exists(directory):
    os.mkdir(directory)

# Create directory to store generated timings xml files.
directory = os.path.join(os.getcwd(), 'output/timings')
if not os.path.exists(directory):
    os.mkdir(directory)

# Create directory to store generated ndofs xml files.
directory = os.path.join(os.getcwd(), 'output/dofs')
if not os.path.exists(directory):
    os.mkdir(directory)

# Create directory to store other outputs files (*pvd, *.pvtu *.xdmf, *.vtu)
directory = os.path.join(os.getcwd(), 'output/others')
if not os.path.exists(directory):
    os.mkdir(directory)

print('Launching demo_poisson on a big core with ndofs = 1 250 000..')
os.system("sudo odroid-smartpower-linux/init")
os.system("mpiexec -n 1 -bind-to user:4 weak-scaling-demo/build/demo_poisson --ndofs=1250000 --xmlname='1_big_core'")
os.system("sudo odroid-smartpower-linux/watthour")
print(' consumed watthour')
timings = convert_table_to_dataframe("output/timings/timings_1_big_core.xml")
value = timings.loc['wall tot']['ZZZ Total']
print(str(value) + " seconds taken to run it.")

print('Launching demo_poisson on a small core with ndofs = 1 250 000..')
os.system("sudo odroid-smartpower-linux/init")
os.system("mpiexec -n 1 -bind-to user:0 weak-scaling-demo/build/demo_poisson --ndofs=1250000 --xmlname='1_small_core'")
os.system("sudo odroid-smartpower-linux/watthour")
print(' consumed watthour')
timings = convert_table_to_dataframe("output/timings/timings_1_small_core.xml")
value = timings.loc['wall tot']['ZZZ Total']
print(str(value) + " seconds taken to run it.")

