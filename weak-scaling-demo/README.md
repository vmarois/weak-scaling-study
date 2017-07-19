FEniCS Simple Weak Scaling Benchmark
====================================

* Prerequisite - FEniCS installation with MPI, PETSc, HDF5

This code is supposed to create a Mesh in the shape of a cube, and
distribute it amongst cores, so that each core has approxiamtely
640000 dofs (values to solve for). It solves the Poisson equation using hypre algebraic multigrid. It should scale well in parallel, and the run time should be fairly constant.

At the end of the run, it prints out some timing statistics, including
timed sections of the main program, shown with "ZZZ" at the start of
the line. It is possible to extract these and plot them - I will
upload a script to do that...

Build
-----

Load the appropriate fenics/dolfin modules, and compile the .ufl file with:

    ffc -l dolfin Poisson.ufl

Then use cmake:

    cmake .
    make

The binary file "demo_poisson" can be run with MPI on any number of
processes. The number of dofs per core can be selected with the
"--ndofs" option (default value 640000). It is also possible to set
the preconditioner and solver with command line options "--pc" and
"--solver". The mesh partitioner is hard-wired to ParMETIS at present,
because PTSCOTCH is not working correctly on Cray with our recent
builds.

The code should work on any number of cores, using the "qsub.bolt"
script. Change the "-l select" line to use more nodes. Obviously this
will vary depending on your system.