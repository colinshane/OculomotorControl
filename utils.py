"""
This file contains a bunch of helper functions.
"""

import numpy as np
import os
import re
import json


def compare_actions_taken(training_params, test_params):
    actions_training = np.loadtxt(training_params['actions_taken_fn'])
    actions_test = np.loadtxt(test_params['actions_taken_fn'])
    n_actions = actions_training[:, 0].size
    for i_ in xrange(n_actions):
        if actions_training[i_, 2] != actions_test[i_, 2]:
            print '\nComparison between actions taken during training and testing diverge in iteration %d: training acion index' % (i_), actions_training[i_, 2], ' test', actions_test[i_, 2]
    get_min_max_gids_for_bg


def get_min_max_gids_for_bg(params, cell_type):
    """
    cell_type -- string possibly values:
        ['d1', 'd2', 'actions', 'supervisor']
    """
    fn = params['bg_gids_fn']
    f = file(fn, 'r')
    d = json.load(f)
    gid_min, gid_max = np.infty, -np.infty
    cell_gids = d[cell_type]
    for gids in cell_gids:
        gid_min = min(gid_min, min(gids))
        gid_max = max(gid_max, max(gids))
    return gid_min, gid_max


def get_colorlist():
    colorlist = ['k', 'b', 'r', 'g', 'm', 'c', 'y', '#FF6600', '#CCFF00', \
            '#808000', '#D35F8D']
    return colorlist

def get_linestyles():
    linestyles = ['-', ':', '--', '-.']
    return linestyles

def get_plus_minus(rnd):
    """
    Returns either -1., or +1. as float.
    rnd -- should be your numpy.random RNG
    """
    return (rnd.randint(-1, 1) + .5) * 2

def extract_trace(d, gid):
    """
    d : voltage trace from a saved with compatible_output=False
    gid : cell_gid
    """
    indices = (d[:, 0] == gid).nonzero()[0]
    time_axis, volt = d[indices, 1], d[indices, 2]
    return time_axis, volt


def merge_and_sort_files(merge_pattern, fn_out, sort=True):
    rnd_nr1 = np.random.randint(0,10**8)
    # merge files from different processors
    tmp_file = "tmp_%d" % (rnd_nr1)
    cmd = "cat %s* > %s" % (merge_pattern, tmp_file)
    print 'utils.merge_and_sort_files: ', cmd
    os.system(cmd)
    # sort according to cell id
    if sort:
        os.system("sort -gk 1 %s > %s" % (tmp_file, fn_out))
    else:
        os.system('mv %s %s' % (tmp_file, fn_out))
    os.system("rm %s" % (tmp_file))
    print 'utils.merge_and_sort_files output: ', fn_out


def find_files(folder, to_match):
    """
    Use re module to find files in folder and return list of files matching the 'to_match' string
    Arguments:
    folder -- string to folder
    to_match -- a string (regular expression) to match all files in folder

    """
    list_of_files = []
    for fn in os.listdir(folder):
        m = re.match(to_match, fn)
        if m:
            list_of_files.append(fn)

    return list_of_files



def get_grid_index_mapping(values, bins):
    """
    Returns a 2-dim array (gid, grid_pos) mapping with values.size length, i.e. the indices of values 
    and the bin index to which each value belongs.
    values -- the values to be put in a grid
    bins -- list or array with the 1-dim grid bins 
    """

    bin_idx = np.zeros((len(values), 2), dtype=np.int)
    for i_, b in enumerate(bins):
#    for i_ in xrange(len(bins)):
#        b = bins[i_]
        idx_in_b = (values > b).nonzero()[0]
        bin_idx[idx_in_b, 0] = idx_in_b
        bin_idx[idx_in_b, 1] = i_
    return bin_idx


def sort_gids_by_distance_to_stimulus(tp, mp, t_start, t_stop, t_cross_visual_field, local_gids=None):
    """
    This function return a list of gids sorted by the distances between cells and the stimulus (in the 4-dim tuning-prop space).
    It calculates the minimal distances between the moving stimulus and the spatial receptive fields of the cells 
    and adds the distances between the motion_parameters and the preferred direction of each cell.

    Arguments:
        tp: tuning_properties array 
        tp[:, 0] : x-pos
        tp[:, 1] : y-pos
        tp[:, 2] : x-velocity
        tp[:, 3] : y-velocity
        mp: motion_parameters (x0, y0, u0, v0, orientation)

    """
    if local_gids == None: 
        n_cells = tp[:, 0].size
    else:
        n_cells = len(local_gids)
    x_dist = np.zeros(n_cells) # stores minimal distance between stimulus and cells
    # it's a linear sum of spatial distance, direction-tuning distance and orientation tuning distance
    for i in xrange(n_cells):
        x_dist[i], spatial_dist = get_min_distance_to_stim(mp, tp[i, :], t_start, t_stop, t_cross_visual_field)

    cells_closest_to_stim_pos = x_dist.argsort()
    if local_gids != None:
        gids_closest_to_stim = local_gids[cells_closest_to_stim_pos]
        return gids_closest_to_stim, x_dist[cells_closest_to_stim_pos]#, cells_closest_to_stim_velocity
    else:
        return cells_closest_to_stim_pos, x_dist[cells_closest_to_stim_pos]#, cells_closest_to_stim_velocity


def get_min_distance_to_stim(mp, tp_cell, t_start, t_stop, t_cross_visual_field): 
    """
    mp : motion_parameters (x, y, u, v, orientation), orientation is optional
    tp_cell : same format as mp
    """
    time = np.arange(t_start, t_stop, 2) # 2 [ms]
    spatial_dist = np.zeros(time.shape[0])
    x_pos_stim = mp[0] + (mp[2] * time + mp[2] * t_start) / t_cross_visual_field
    y_pos_stim = mp[1] + (mp[3] * time + mp[3] * t_start) / t_cross_visual_field
    spatial_dist = (tp_cell[0] - x_pos_stim)**2 + (tp_cell[1] - y_pos_stim)**2
    min_spatial_dist = np.sqrt(np.min(spatial_dist))

    velocity_dist = np.sqrt((tp_cell[2] - mp[2])**2 + (tp_cell[3] - mp[3])**2)

    dist =  min_spatial_dist + velocity_dist
    return dist, min_spatial_dist
    

def get_spiketimes(all_spikes, gid, gid_idx=0, time_idx=1):
    """
    Returns the spikes fired by the cell with gid
    all_spikes: 2-dim array containing all spiketimes
    gid_idx: is the column index in the all_spikes array containing GID information
    time_idx: is the column index in the all_spikes array containing time information
    """
    idx_ = (all_spikes[:, gid_idx] == gid).nonzero()[0]
    spiketimes = all_spikes[idx_, time_idx]
    return spiketimes


def communicate_local_spikes(gids, comm):

    my_nspikes = {}
    for i_, gid in enumerate(gids):
        my_nspikes[gid] = (gids == gid).nonzero()[0].size
    
    all_spikes = [{} for pid in xrange(comm.size)]
    all_spikes[comm.rank] = my_nspikes
    for pid in xrange(comm.size):
        all_spikes[pid] = comm.bcast(all_spikes[pid], root=pid)
    all_nspikes = {} # dictionary containing all cells that spiked during that iteration
    for pid in xrange(comm.size):
        for gid in all_spikes[pid].keys():
#            gid_ = gid
            gid_ = gid - 1
            all_nspikes[gid_] = all_spikes[pid][gid]
    gids_spiked = np.array(all_nspikes.keys(), dtype=np.int)
    nspikes =  np.array(all_nspikes.values(), dtype=np.int)
    comm.barrier()
    return gids_spiked, nspikes


def filter_connection_list(d):
    """
    d -- 3 columnar connection list:
      src     tgt     weight
    returns only those rows with weight != 0
    """
    valid_idx = (d[:, 2] != 0).nonzero()[0]
    return d[valid_idx, :]

