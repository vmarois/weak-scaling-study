FEniCS Simple Weak Scaling Benchmark Plot
=========================================

This code is relying on the Weak Scaling Benchmark by [Chris Richardson](https://bitbucket.org/chris_richardson/weak-scaling-demo), and is focused on plotting various timings outputted by the test.

## Introduction
The initial context for this repository is the assesment of FEniCS performance on ARM-based architectures. We are currently using the [Odroid XU4](http://www.hardkernel.com/main/products/prdt_info.php),
which is a rather powerful ARM SBC, running on the *Samsung Exynos 5422* processor, which has 4 x *Cortex™-A15* @ 2Ghz and 4 x *Cortex™-A7* CPUs. 

For now, we are focusing on studying the time taken to complete the `weak-scaling-demo` benchmark depending on which combination of CPUs is used. To illustrate, we are considering the following combinations:

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

After the build is complete, you can use the following `python` scripts :

* `xml_generation.py` will run the benchmark using the CPUs combinations indicated. The results (timings of various steps) are outputted to xml files, stored in `weak-scaling-demo/xmlfiles`.
* `timings_plot.py` will read in the xml files and produce plots saved to PDF.
