#!/bin/bash -l
# The -l above is required to get the full environment with modules

# The name of the script is myjob
#SBATCH -J RBL_long_0

# Only 1 hour wall-clock time will be given to this job
#SBATCH -t 04:25:00

# Number of cores to be allocated (multiple of 40)
#SBATCH -N 3
#SBATCH -n 120
#SBATCH --ntasks-per-node=40

#SBATCH -e error_file_RBL.e
#SBATCH -o output_file_RBL.o

echo "Starting at `date`"
export CRAY_ROOTFS=DSL

#. /opt/modules/default/etc/modules.sh
module swap PrgEnv-cray PrgEnv-gnu
module add nest/2.2.2
module add python

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/cfs/milner/scratch/b/bkaplan/BCPNN-Module/build-module-100725
export PYTHONPATH=/pdc/vol/nest/2.2.2/lib/python2.7/site-packages:/pdc/vol/python/2.7.6-gnu/lib/python2.7/site-packages

# EITHER START NEW TRAINING:
#aprun -n 120 -N 40 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py [TRAINING_STIMULI_FILE] 0 > delme_rbl_0 2>&1

# e.g.
#aprun -n 120 -N 40 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py training_stimuli_nV11_nX7.dat 0 > delme_rbl_0 2>&1

# OR CONTINUE TRAINING
#aprun -n 120 -N 40 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py [OLD_FOLDER] [NEW_FOLDER] [TRAINING_STIMULI_FILE] [STIM_IDX_TO_CONTINUE] > delme_rbl_0 2>&1

# e.g.
#aprun -n 120 -N 40 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py Training_RBL_withMpnNoise_titer25_nStim2_0-2_gain1.00_seeds_111_1  Training_RBL_withMpnNoise_titer25_nStim2_2-4_gain1.00_seeds_111_1/ training_stimuli_nV11_nX7.dat 2 > delme_rbl_2 2>&1

aprun -n 120 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py Training_RBL_withMpnNoise_titer25_nStim10_6-16_gain1.00_seeds_111_1  Training_RBL_withMpnNoise_titer25_nStim10_16-26_gain1.00_seeds_111_1/ training_stimuli_nV11_nX7.dat 16 > delme_rbl_16 2>&1
aprun -n 120 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py Training_RBL_withMpnNoise_titer25_nStim10_16-26_gain1.00_seeds_111_1/ Training_RBL_withMpnNoise_titer25_nStim10_26-36_gain1.00_seeds_111_1/ training_stimuli_nV11_nX7.dat 26 > delme_rbl_26 2>&1
aprun -n 120 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py Training_RBL_withMpnNoise_titer25_nStim10_26-36_gain1.00_seeds_111_1/ Training_RBL_withMpnNoise_titer25_nStim10_36-46_gain1.00_seeds_111_1/ training_stimuli_nV11_nX7.dat 36 > delme_rbl_36 2>&1
aprun -n 120 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py Training_RBL_withMpnNoise_titer25_nStim10_36-46_gain1.00_seeds_111_1/ Training_RBL_withMpnNoise_titer25_nStim10_46-56_gain1.00_seeds_111_1/ training_stimuli_nV11_nX7.dat 46 > delme_rbl_46 2>&1
aprun -n 120 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py Training_RBL_withMpnNoise_titer25_nStim10_46-56_gain1.00_seeds_111_1/ Training_RBL_withMpnNoise_titer25_nStim10_56-66_gain1.00_seeds_111_1/ training_stimuli_nV11_nX7.dat 56 > delme_rbl_56 2>&1
aprun -n 120 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py Training_RBL_withMpnNoise_titer25_nStim10_56-66_gain1.00_seeds_111_1/ Training_RBL_withMpnNoise_titer25_nStim10_66-76_gain1.00_seeds_111_1/ training_stimuli_nV11_nX7.dat 66 > delme_rbl_66 2>&1
aprun -n 120 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py Training_RBL_withMpnNoise_titer25_nStim10_66-76_gain1.00_seeds_111_1/ Training_RBL_withMpnNoise_titer25_nStim10_76-86_gain1.00_seeds_111_1/ training_stimuli_nV11_nX7.dat 76 > delme_rbl_76 2>&1

echo "Stopping at `date`"


