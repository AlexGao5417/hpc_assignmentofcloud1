#!/bin/bash
#SBATCH -p physical
#SBATCH --time=00:15:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=1n1c.out

module load Python/3.5.2-goolf-2015a

time mpiexec python3 assignment1.py
