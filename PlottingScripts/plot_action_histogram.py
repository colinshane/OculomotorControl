import os, sys, inspect
# use this if you want to include modules from a subforder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
import simulation_parameters
import utils
import numpy as np
import json
import pylab
import FigureCreator


plot_params = {'backend': 'png',
              'axes.labelsize': 20,
              'axes.titlesize': 20,
              'text.fontsize': 20,
              'xtick.labelsize': 20,
              'ytick.labelsize': 20,
              'legend.pad': 0.2,     # empty space around the legend box
              'legend.fontsize': 16,
               'lines.markersize': 1,
               'lines.linewidth': 3,
              'path.simplify': False,
              'figure.subplot.left' : 0.17, 
              'figure.subplot.bottom' : 0.08, 
              'figure.subplot.right' : 0.97, 
              'figure.subplot.top' : 0.92, 
              'figure.subplot.hspace' : 0.45,
              } 
#              'figure.figsize': FigureCreator.get_fig_size(800, portrait=False)}

pylab.rcParams.update(plot_params)

#folder = 'Training_nRF500_expSyn_d1recFalse_nStim10x20_it25_tsim40000_taup20000//'
folder = os.path.abspath(sys.argv[1])
params = utils.load_params(folder)
d = np.loadtxt(params['actions_taken_fn'])

figsize=FigureCreator.get_fig_size(1200, portrait=True)
print 'figsize:', figsize
fig = pylab.figure(figsize=figsize)
ax1 = fig.add_subplot(411)
ax1.set_title('Histogram of actions taken during training')
print 'n_actions', params['n_actions']
print 'd:', d[:, 2]
cnt, bins = np.histogram(d[:, 2], bins=params['n_actions'], range=(0, params['n_actions']))
print 'bins', bins
ax1.bar(bins[:-1], cnt, width=bins[1]-bins[0])
ax1.set_xlabel('Actions taken')
ax1.set_ylabel('Count')
ax1.set_xlim((0, params['n_actions']))


d_conn = np.loadtxt(params['mpn_bgd1_merged_conn_fn'])
f_bg = file(params['bg_gids_fn'], 'r')
bg_cell_gids = json.load(f_bg)


w_in = {}
w_in_mean = np.zeros(params['n_actions'])
w_in_std = np.zeros(params['n_actions'])
w_in_sum = np.zeros(params['n_actions'])
n_in_mean = np.zeros(params['n_actions'])
n_in_std = np.zeros(params['n_actions'])

for i_a in xrange(params['n_actions']):
    action_gids = bg_cell_gids['d1'][i_a]
    w_in[i_a] = {}
    w_in[i_a]['w_in_mean_cells'] = np.zeros(params['num_msn_d1'])
    w_in[i_a]['w_in_std_cells'] = np.zeros(params['num_msn_d1'])

    n_in = np.zeros(params['num_msn_d1'])
    all_source_gids = []
    for i_cell, gid in enumerate(action_gids):
        sources = utils.get_sources(d_conn, gid)
        all_source_gids += sources[:, 0].tolist()
        w_in[i_a]['w_in_mean_cells'][i_cell] = sources[:, 2].mean()
        w_in[i_a]['w_in_std_cells'][i_cell] = sources[:, 2].std()
        w_in_sum[i_a] += sources[:, 2].sum()
        n_in[i_cell] = sources[:, 0].size
    w_in_mean[i_a] = w_in[i_a]['w_in_mean_cells'].mean()
    w_in_std[i_a] = w_in[i_a]['w_in_mean_cells'].std()
    n_in_mean[i_a] = n_in.mean()
    n_in_std[i_a] = n_in.std()
    print 'w_in_mean[%d]: %.3f +- %.3f' % (i_a, w_in_mean[i_a], w_in_std[i_a])

    print 'Num VisualLayer sources to action %d: ' % (i_a), np.unique(all_source_gids).size

ax2 = fig.add_subplot(412)
ax2.bar(range(params['n_actions']), w_in_mean, yerr=w_in_std)
ax2.set_xlabel('Action')
ax2.set_ylabel('Mean incoming\nweight to D1')
ax2.set_xlim((0, params['n_actions']))


ax3 = fig.add_subplot(413)
ax3.bar(range(params['n_actions']), w_in_sum)
ax3.set_xlabel('Action')
ax3.set_ylabel('Sum of incoming\nweights to D1')
ax3.set_xlim((0, params['n_actions']))

ax4 = fig.add_subplot(414)
ax4.bar(range(params['n_actions']), n_in_mean, yerr=n_in_std)
ax4.set_xlabel('Action')
ax4.set_ylabel('Num of incoming\nconnections per D1 nrn')
ax4.set_xlim((0, params['n_actions']))


output_fn = params['figures_folder'] + 'action_histogram.png'
print 'Saving to:', output_fn
pylab.savefig(output_fn)

pylab.show()