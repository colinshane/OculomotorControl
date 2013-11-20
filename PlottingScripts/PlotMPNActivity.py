import os, sys, inspect
# use this if you want to include modules from a subforder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../")))
print 'cmd_subfolder', cmd_subfolder
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import sys
import os
import utils
import re
import numpy as np
import pylab
import matplotlib


class ActivityPlotter(object):

    def __init__(self, params, it_max=None):
        self.params = params
        if it_max == None:
            self.it_max = self.params['n_iterations']
        else:
            self.it_max = it_max

        self.n_bins_x = 30
        self.n_x_ticks = 10
        self.x_ticks = np.linspace(0, self.n_bins_x, self.n_x_ticks)
        self.load_tuning_prop()


    def load_tuning_prop(self):
        print 'ActivityPlotter.load_tuning_prop ...'
        self.tuning_prop_exc = np.loadtxt(self.params['tuning_prop_exc_fn'])
        self.tuning_prop_inh = np.loadtxt(self.params['tuning_prop_inh_fn'])

        self.x_grid = np.linspace(0, 1, self.n_bins_x, endpoint=False)
        self.gid_to_posgrid_mapping = utils.get_grid_index_mapping(self.tuning_prop_exc[:, 0], self.x_grid)



    def plot_input(self):
        d = np.zeros((self.it_max, self.x_grid.size)) #self.x_grid.size, self.it_max))

        for iteration in xrange(self.it_max):
            print 'Plot input iteration', iteration
            fn_to_match = (self.params['input_nspikes_fn_mpn'] + 'it%d_' % iteration).rsplit('/')[-1]
            list_of_files = utils.find_files(self.params['input_folder_mpn'], fn_to_match)
            for fn_ in list_of_files:
                fn = self.params['input_folder_mpn'] + fn_
                print 'Loading:', fn
                d_it = np.loadtxt(fn, dtype=np.int)
                nspikes = d_it[:, 1]

                for i_gid in xrange(d_it[:, 0].size):
                    gid = d_it[i_gid, 0]
                    # map the gids to their position in the xgrid
                    xpos = self.gid_to_posgrid_mapping[gid, 1]
                    d[iteration, xpos] += d_it[i_gid, 1]
#                    if d_it[i_gid, 1] > 0:
#                        print 'gid %d xpos %d nspikes_input %d' % (gid, xpos, d_it[i_gid, 1])
                    

        d /= self.params['t_iteration'] / 1000.
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        cax = ax.pcolormesh(d)#, cmap='binary')

        if self.params['training']:
            testtraining = 'training'
        else:
            testtraining = 'testing'

        ax.set_title('Input spikes during %s' % testtraining)
        ax.set_ylim((0, d.shape[0]))
        ax.set_xlim((0, d.shape[1]))
        ax.set_ylabel('Iteration')
        ax.set_xlabel('x-pos')
        cbar = pylab.colorbar(cax)
        cbar.set_label('Input rate [Hz]')

        xlabels = ['%.1f' % (float(xtick) / self.n_bins_x) for xtick in self.x_ticks]
        ax.set_xticks(self.x_ticks)
        ax.set_xticklabels(xlabels)
        output_fn = self.params['data_folder'] + 'mpn_input_activity.dat'
        print 'Saving data to:', output_fn
        np.savetxt(output_fn, d)

        output_fig = self.params['figures_folder'] + 'mpn_input_activity.png'
        print 'Saving figure to:', output_fig
        pylab.savefig(output_fig)

    
#    def get_nspikes(self, merged_spike_fn):
#        d = np.loadtxt(merged_spike_fn)
#        nspikes = np.zeros(self.params['n_exc_mpn'])
#        for gid in xrange(1, self.params['n_exc_mpn'] + 1):
#            idx = (d[:, 0] == gid).nonzero()[0]
#            nspikes[gid - 1] = idx.size
#        return nspikes


    def get_nspikes_interval(self, d, t0, t1):
        """
        d -- np.array containg the spike times (col 0 - gids, col 1 - times)
        """

        nspikes = np.zeros(self.params['n_exc_mpn'])
        for gid in xrange(1, self.params['n_exc_mpn'] + 1):
            cell_spikes = d[(d[:, 0] == gid).nonzero()[0], 1]
            idx = ((cell_spikes >= t0) == (cell_spikes <= t1)).nonzero()[0]
            nspikes[gid - 1] = idx.size
#            print 'cell %d spikes between %d - %d: %d times' % (gid, t0, t1, nspikes[gid - 1])
        return nspikes


    def plot_output(self):
        merged_spike_fn = self.params['spiketimes_folder_mpn'] + self.params['mpn_exc_spikes_fn_merged']
        utils.merge_and_sort_files(self.params['spiketimes_folder_mpn'] + self.params['mpn_exc_spikes_fn'], merged_spike_fn)
        spike_data = np.loadtxt(merged_spike_fn)
        d = np.zeros((self.it_max, self.x_grid.size)) #self.x_grid.size, self.it_max))
        nspikes_thresh = 1
        for iteration in xrange(self.it_max):
            print 'Plot output iteration', iteration
            cells_per_grid_cell = np.zeros(self.x_grid.size) # how many cells have been above a threshold activity during this iteration
            t0, t1 = iteration * self.params['t_iteration'], (iteration + 1) * self.params['t_iteration']
            nspikes = self.get_nspikes_interval(spike_data, t0, t1) 
            for gid in xrange(self.params['n_exc_mpn']):
                xpos = self.gid_to_posgrid_mapping[gid, 1]
                d[iteration, xpos] += nspikes[gid]
                if nspikes[gid] > nspikes_thresh:
                    cells_per_grid_cell[xpos] += 1
            for grid_idx in xrange(self.x_grid.size):
                if cells_per_grid_cell[grid_idx] > 0:
                    d[iteration, grid_idx] /= cells_per_grid_cell[grid_idx]

        d /= self.params['t_iteration'] / 1000.
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        cax = ax.pcolormesh(d)#, cmap='binary')

        if self.params['training']:
            testtraining = 'training'
        else:
            testtraining = 'testing'

        ax.set_title('Output spikes during %s clustered by x-pose' % testtraining)
        ax.set_ylim((0, d.shape[0]))
        ax.set_xlim((0, d.shape[1]))
        ax.set_ylabel('Iteration')
        ax.set_xlabel('x-pos')
        cbar = pylab.colorbar(cax)
        cbar.set_label('Output rate [Hz]')

        xlabels = ['%.1f' % (float(xtick) / self.n_bins_x) for xtick in self.x_ticks]
        ax.set_xticks(self.x_ticks)
        ax.set_xticklabels(xlabels)
        output_fn = self.params['data_folder'] + 'mpn_output_activity.dat'
        print 'Saving data to:', output_fn
        np.savetxt(output_fn, d)

        output_fig = self.params['figures_folder'] + 'mpn_output_activity.png'
        print 'Saving figure to:', output_fig
        pylab.savefig(output_fig)


    def plot_retinal_slip(self):
        print 'plot_retinal_slip loads:', self.params['motion_params_fn']
        d = np.loadtxt(self.params['motion_params_fn'])
        t = d[:, 4]
        x_slip = np.abs(d[:, 0] - .5)
        output_fn = self.params['data_folder'] + 'mpn_xslip.dat'
        print 'Saving data to:', output_fn
        np.savetxt(output_fn, d)

        fig = pylab.figure()
        ax = fig.add_subplot(111)
        ax.plot(t, x_slip)

        ymin, ymax = x_slip.min(), x_slip.max()
        for it_ in xrange(self.params['n_iterations']):
            t0 = it_ * self.params['t_iteration']
#            t1 = (it_ + 1) * self.params['t_iteration']
            ax.plot((t0, t0), (ymin, ymax), ls='-.', c='k')

        ax.set_xlabel('Time [ms]')
        ax.set_ylabel('Retinal slip (x-dim)')
        output_fig = self.params['figures_folder'] + 'mpn_slip.png'
        print 'Saving figure to:', output_fig
        pylab.savefig(output_fig)


    def plot_raster_sorted(self, title='', cell_type='exc', sort_idx=0):
        """
        sort_idx : the index in tuning properties after which the cell gids are to be sorted for  the rasterplot
        """
        if cell_type == 'exc':
            tp = self.tuning_prop_exc
        else:
            tp = self.tuning_prop_ing

        tp_idx_sorted = tp[:, sort_idx].argsort() # + 1 because nest indexing

        merged_spike_fn = self.params['spiketimes_folder_mpn'] + self.params['mpn_exc_spikes_fn_merged']
        spikes_unsrtd = np.loadtxt(merged_spike_fn)

        fig = pylab.figure()
        ax = fig.add_subplot(111)
        ax.set_title(title)
        for i_, gid in enumerate(tp_idx_sorted):
            spikes = utils.get_spiketimes(spikes_unsrtd, gid + 1)
            nspikes = spikes.size
            y_ = np.ones(spikes.size) * tp[gid, sort_idx]
            ax.plot(spikes, y_, 'o', markersize=3, color='k')

        return fig, ax


    def plot_input_spikes_sorted(self, ax=None, title='', sort_idx=0):
        """
        Input spikes are stored in seperate files for each cell and for each iteration.
        --> filenames are Folder/InputSpikes_MPN/input_spikes_X_GID.dat X = iteration, GID = cell gid
        """
        print 'plotting input spikes ...'

        if ax == None:
            fig = pylab.figure()
            ax = fig.add_subplot(111)
            ax.set_title(title)

        tp = self.tuning_prop_exc
        tp_idx_sorted = tp[:, sort_idx].argsort() # + 1 because nest indexing

        for fn in os.listdir(self.params['input_folder_mpn']):
            m = re.match('input_spikes_(\d+)_(\d+).dat', fn)
            if m:
                iteration = int(m.groups()[0])
                gid = int(m.groups()[1])
                y_pos_of_cell = tp[gid, sort_idx]
                fn_ = self.params['input_folder_mpn'] + fn
                d = np.loadtxt(fn_)
                ax.plot(d, y_pos_of_cell * np.ones(d.size), 'o', markersize=3, alpha=.1, color='b')


if __name__ == '__main__':

    if len(sys.argv) > 1:
        param_fn = sys.argv[1]
        if os.path.isdir(param_fn):
            param_fn += '/Parameters/simulation_parameters.json'
        import json
        f = file(param_fn, 'r')
        print 'Loading parameters from', param_fn
        params = json.load(f)

    else:
        import simulation_parameters
        param_tool = simulation_parameters.global_parameters()
        params = param_tool.params

    
    utils.merge_and_sort_files(params['spiketimes_folder_mpn'] + params['mpn_exc_spikes_fn'], params['spiketimes_folder_mpn'] + params['mpn_exc_spikes_fn_merged'])
    Plotter = ActivityPlotter(params)#, it_max=1)
    Plotter.plot_input()
    Plotter.plot_output()
#    Plotter.plot_retinal_slip()
    fig, ax = Plotter.plot_raster_sorted(title='Exc cells sorted by x-position', sort_idx=0)
    Plotter.plot_input_spikes_sorted(ax, sort_idx=0)
    fig.savefig(params['figures_folder'] + 'rasterplot_mpn_in_and_out.png')

#    Plotter.plot_raster_sorted(title='Exc cells sorted by $v_x$', sort_idx=2)
    pylab.show()