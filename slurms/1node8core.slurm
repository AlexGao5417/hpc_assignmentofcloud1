#!/bin/bash
#SBATCH --partition=physical
#SBATCH --time=00:15:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=1
#SBATCH --output=1n8c.out

module load Python/3.5.2-goolf-2015a

time mpiexec python3 assignment1.py
