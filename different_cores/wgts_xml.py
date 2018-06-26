import os
import subprocess

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


# Generate the appropriate command for the weak-scaling test and then run it.
# The number of dofs is constant and fixed to 120000 (maximum value without crashing).

# Construct the command to pass to os.system()
init_meter = "sudo odroid-smartpower-linux/init"
generate_xml = "mpirun -n 8 -bind-to core weak-scaling-demo/build/demo_poisson --ndofs=120000 --xmlname=wgts_distributed"
get_watthour = "sudo odroid-smartpower-linux/watthour"

# Run the command
os.system(init_meter)  # Reinitializes the wattmeter and starts the watthour measures.
os.system(generate_xml)  # Run demo_poisson with mpiexec and the specific core combinations.
os.system(get_watthour) # Prints the current watthour measure.
