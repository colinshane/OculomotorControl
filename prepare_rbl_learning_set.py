import numpy as np 
import simulation_parameters
import os
import subprocess
import time


def prepare_simulation(ps, params):
    folder_name = params['folder_name']
    print 'DEBUG prepare_simulation', params['folder_name']
    ps.set_filenames(folder_name)
    ps.create_folders()
    param_fn = ps.params['params_fn_json']
    print 'Debug prepare_simulation folder written to file', ps.params['data_folder']
    print 'Ready for simulation:\n\t%s' % (param_fn)
    ps.write_parameters_to_file(fn=param_fn)
    #time.sleep(1.)


def run_simulation(training_folder, test_folder, USE_MPI):
    # specify your run command (mpirun -np X, python, ...)
#    parameter_filename = params['params_fn_json']

    if USE_MPI:
        reply = subprocess.check_output(['grep', 'processor', '/proc/cpuinfo'])
        n_proc = reply.count('processor')
        print 'reply', n_proc
        run_command = 'mpirun -np %d python main_testing.py %s %s' % (n_proc, training_folder, test_folder)
    else:
        run_command = 'python main_testing.py %s %s' % (training_folder, test_folder)
    print 'Running:\n\t%s' % (run_command)
    os.system(run_command)



if __name__ == '__main__':

    try:
        from mpi4py import MPI
        USE_MPI = True
        comm = MPI.COMM_WORLD
        pc_id, n_proc = comm.rank, comm.size
        print "USE_MPI:", USE_MPI, 'pc_id, n_proc:', pc_id, n_proc
    except:
        USE_MPI = False
        pc_id, n_proc, comm = 0, 1, None
        print "MPI not used"

#    USE_MPI = False

    #training_params_fn = 'training_stimuli_900_3step_nonshuffled.txt'
    #training_params_fn = 'training_stim_params_3steps300stim.txt'
    training_params_fn = 'training_stimuli_900_0.3center_0.7center.txt'
    ps = simulation_parameters.global_parameters()

    n_jobs = 9
    n_stimuli_per_run = 30
    stim_offset = 30
    
    seed_folder = "Training__nactions17_delayIn0_out0_nStim30_0-30_gainD1_0.8_D2_0.8_K1_-1_seeds_321_5"

    aprun_cmd_base = 'aprun -n 240 python /cfs/milner/scratch/b/bkaplan/OculomotorControl/main_training_reward_based_new.py'

    run_commands = []
    old_folder = seed_folder
    for i_ in xrange(0, n_jobs):
        params = ps.params
        if params['training'] == False:
            print 'set training = True'
            exit(1)
        stim_range = (i_ * n_stimuli_per_run + stim_offset, (i_ + 1) * n_stimuli_per_run + stim_offset) 
        params['stim_range'] = [stim_range[0], stim_range[1]]
        params['master_seed'] = 111 + params['stim_range'][0]
        folder_name = 'Training_%s_nStim%d_%d-%d_gainD1_%.1f_D2_%.1f_K%d_%d_seeds_%d_%d/' % (params['sim_id'], \
                params['n_stim_training'], params['stim_range'][0], params['stim_range'][1], 
                params['gain_MT_d1'], params['gain_MT_d2'], params['pos_kappa'], params['neg_kappa'], params['master_seed'], params['visual_stim_seed'])
        params['folder_name'] = folder_name
        print 'folder_name:', folder_name
        assert (params['n_stim_training'] == n_stimuli_per_run), 'ERROR: make sure that n_training_x/v match your desired number of simulations to be run!'
        prepare_simulation(ps, params)

        stim_idx = stim_offset + i_ * n_stimuli_per_run
        new_cmd = ' %s %s %s %d > delme_rbl_gD1%.1f_gD2%.1fK%d_%d_tmp%.1f_%d_%dactions 2>&1' % (old_folder, folder_name, training_params_fn, stim_idx, params['gain_MT_d1'], params['gain_MT_d2'], \
                params['pos_kappa'], params['neg_kappa'], params['softmax_action_selection_temperature'], stim_idx, params['n_actions'])
        aprun_cmd = aprun_cmd_base + new_cmd
        old_folder = folder_name

        run_commands.append(aprun_cmd)

    for i_ in xrange(len(run_commands)):
        print run_commands[i_]

