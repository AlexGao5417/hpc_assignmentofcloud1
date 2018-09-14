# HPC_Instagram_GeoProcessing

**A simple, parallelized application leveraging the University of Melbourne HPC facility SPARTAN.**
## Usage
Using `ssh` to login to SPARTAN and execute 3 different scripts (in the 'slurms' folder) below to submit the job:  

`sbatch 1node1core.slurm` *to run with 1 node 1 core* 

`sbatch 1node8core.slurm` *to run with 2 nodes 8 cores*   

`sbatch 2node8core.slurm` *to run with 2 nodes 8 cores*  


> *Note:* The output is in the `out_files` folder.  
  
## Summary
* Using the same number of nodes but more cores to parallelize a single job can reduce the processing   time significantly. For this assignment, using 1 node 8 cores or 2 nodes 8 cores can reduce approximately 58% execution time comparing with 1 node 1 core.
* Using the same number of cores but more nodes may not affect the processing time. However, as shown in Fig 7, using 2 nodes takes 2 more seconds than 1 node under 8 cores. I think there might be two reasons. First, nodes need to communicate with each other so they can work together, which might take a little bit time; Second, the SPARTAN is a shared network system so servers on it might be volatile.

