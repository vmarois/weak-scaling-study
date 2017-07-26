FEniCS Simple Weak Scaling Benchmark Plot
=========================================

This code is relying on the Weak Scaling Benchmark by [Chris Richardson](https://bitbucket.org/chris_richardson/weak-scaling-demo), and is focused on plotting various timings outputted by the test.

## Introduction
The initial context for this repository is the assesment of FEniCS performance on ARM-based architectures. We have been using the [Odroid XU4](http://www.hardkernel.com/main/products/prdt_info.php),
which is a rather powerful ARM SBC, running on the *Samsung Exynos 5422* processor, which has 4 x *Cortex™-A15* @ 2Ghz and 4 x *Cortex™-A7* CPUs. 

For now, we are focusing on studying the time taken to complete the several stages of the `weak-scaling-demo` benchmark depending on which combination of CPUs is used. To illustrate, we are considering the following combinations:

* All 8 cores
* All 4 *Cortex™-A15*
* All 4 *Cortex™-A7*
* And other combinations, e.g. 1 x *Cortex™-A15* + 1 x *Cortex™-A7*.

## Build

You'll first need to build the `weak-scaling-demo` test :

    cd weak-scaling-demo
    ffc -l dolfin Poisson.ufl
    mkdir build
    cd build
    cmake ../
    make

You'll also need to install some additionnals `python` modules :

    pip3 install -r requirements.txt


## Scripts organization

After the build is complete, several `python` scripts can be used.
You'll find 2 folders containing various scripts :

* `different_cores`, which is aimed at processors made of 2 types of CPUs, just like ARM architectures. Here, it is interesting to see the difference in performance when using only the big CPUs or only the small ones for instance.
* `similar_cores`, which is aimed at processors made of 1 type of CPUs, like the x86 (Intel) ones. Here, we are more interested in the performance when increasing the number of processes, to compare it to the similar results produced on ARM architectures.

You can use the following command to  print some info about the CPUS of your machine :

    cat /proc/cpuinfo

Hence, in both folders, you'll find 2 scripts `linear_scaling_xml.py` & `linear_scaling_plot.py`:
* The first one will run the benchmark, increasing each time the number of processes run (in a balanced way, meaning that for processors with different cores, the number of processes on the small cores & on the big ones are always equal). The results are outputted to xml files, stored in `/xmlfiles`.
* The second script will produces 2 plots, by reading in the xml files produced : the timings of the various stages of the benchmark in function of the number of processes run, and the *efficiency* of the benchmark, as defined [here](https://www.sharcnet.ca/help/index.php/Measuring_Parallel_Scaling_Performance#Weak_Scaling).

Finally, for the `different_cores` folder, you'll also find the scripts `cores_combinations_xml.py` & `cores_combinations_plot.py`, the first one running the benchmark using the different cores combinations specified (see example above), the second one plotting the timings of the different stages of the benchmark in function of the cores combinations used.
The plots are saved as pdf, stored in `/pdf`.

If you would like to change the cores combinations used to run the benchmark, you can do so by modifying the `cores_combinations` & `labels` variables in the scripts cited above.
