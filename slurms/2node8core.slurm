#!/bin/bash
#SBATCH --partition=physical
#SBATCH --time=00:30:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --output=2n8c.out

module load Python/3.5.2-goolf-2015a

time mpiexec python3 assignment1.py
