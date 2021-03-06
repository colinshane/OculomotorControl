"""
script possibly deprecated, worked with get_reward_gauss, but return value of get_reward_sigmoid returns only R and no other parameters
"""

import numpy as np
import pylab
import utils
import simulation_parameters
import BasalGanglia
import utils
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
from matplotlib import cm
from PlottingScripts.FigureCreator import plot_params, get_fig_size


def plot_reward_schedule_random(x, R):

    fig = pylab.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()
    N = len(x)
    for i_ in xrange(N):
        ax1.plot(i_, x[i_], 'o', markersize=10, c='k')
    ax1.plot(range(N), x, '-', ls='-', c='k', lw=2)

    ms_min = 2
    ms_max = 10
    for i_ in xrange(N - 1):
        if R[i_] > 0:
            c = 'r'
            s = '^'
            fillstyle = 'full'
        else:
            c = 'b'
            s = 'v'
            fillstyle = 'full' #'none'
        ms = np.abs(np.round(R[i_] / np.max(R) * ms_max)) + ms_min
        print 'R i_ markersize', R[i_], i_, ms
        ax2.plot(i_, R[i_], s, markersize=ms, c=c, fillstyle=fillstyle)

    ax1.plot((-.5, N + .5), (.5, .5), '--', c='k')
    ax1.set_xlim(-.5, N + .5)
    ax1.set_ylim((-.1, 1.1))

    fs = 18
    ax1.set_title('Reward schedule for random actions & positions', fontsize=fs)
    ax1.set_xlabel('Iteration', fontsize=fs)
    ax1.set_ylabel('Position', fontsize=fs)
    ax2.set_ylabel('Reward', fontsize=fs)


def get_reward(dx, dx_abs, dj_di_abs):
    n_it = dx.size
    R = np.zeros(n_it - 1)
    A = 1# amplify the improvement / worsening linearly
    B = .7  # punish overshoot, 0 <= B <= 1.
    for i_ in xrange(1, n_it):
        print 'i_ R, dj_di_abs', i_, R.size, dj_di_abs.size, i_ - 1
#        R[i_-1] = -1 * A * dj_di_abs[i_-1] * np.abs(dj_di_abs[i_-1])
        R[i_-1] = -2. * A * dj_di_abs[i_-1]
        if np.sign(dx[i_-1]) != np.sign(dx[i_]):
            R[i_-1] *= B
    return R


def test_random_placements():
    np.random.seed(0)
    n_iterations = 30
    x = np.zeros(n_iterations)
    for i_ in xrange(n_iterations):
        x[i_] = np.random.rand()
    dx = x - .5
    dx_abs = np.abs(dx)
    dj_di_abs = dx_abs[1:] - dx_abs[:-1]
    #R = get_reward(dx, dx_abs, dj_di_abs)
    R = np.zeros(n_iterations)
    for i_ in xrange(n_iterations-1):
        R[i_] = utils.get_reward_from_perceived_states(x[i_], x[i_+1])
    print 'Iteration x\tdx\tdx_abs\tdj_di_abs\tReward'
    for i_ in xrange(1, n_iterations):
        print '%2d\t%.2f\t%.2f\t%.2f' % (i_-1, x[i_-1], dx[i_-1], dx_abs[i_-1])
        print '%2d\t%.2f\t%.2f\t%.2f\t%.2f\t\t%.2f' % (i_, x[i_], dx[i_], dx_abs[i_], dj_di_abs[i_-1], R[i_-1])
        print '\n'
    plot_reward_schedule_random(x, R)
    pylab.savefig('Reward_schedule_with_random_positions_and_random_actions.png', dpi=200)


def get_rewards_for_all_stimuli_and_actions(n_pos=20, n_v=20):

    v_min = 0.
    v_max =  2.
    GP = simulation_parameters.global_parameters()
    params = GP.params
    BG = BasalGanglia.BasalGanglia(params, dummy=True)
    speeds = BG.action_bins_x

    x_pos = np.linspace(0., 1., n_pos)
    vx = np.linspace(v_min, v_max, n_v)
    print 'x_pos:', x_pos

#    R = np.zeros((n_pos, n_pos, n_v, params['n_actions']))
    stimuli_and_rewards = np.zeros((n_pos * n_v * params['n_actions'], 6))
    idx = 0
    for i_x in xrange(n_pos):
        x_old = x_pos[i_x]
        for i_v in xrange(n_v):
            stim_params = [x_pos[i_x], .5, vx[i_v], 0.]
            for i_a in xrange(params['n_actions']):
                x_new = utils.get_next_stim(params, stim_params, speeds[i_a])[0]
#                R = utils.get_reward_from_perceived_states(x_old, x_new)
#                R, sigma_R = utils.get_reward_gauss(x_new, stim_params, params)
                R = utils.get_reward_sigmoid(x_new, stim_params, params)
                #R = utils.get_reward_from_perceived_states(x_old, x_new)
                stimuli_and_rewards[idx, 0] = x_old
                stimuli_and_rewards[idx, 1] = x_new
                stimuli_and_rewards[idx, 2] = vx[i_v]
                stimuli_and_rewards[idx, 3] = i_a
                stimuli_and_rewards[idx, 4] = speeds[i_a]
                stimuli_and_rewards[idx, 5] = R
                idx += 1


    return stimuli_and_rewards

#    print "BG.action_bins_x:", BG.action_bins_x


def plot_4d(d):

    fig = pylab.figure()
    ax = Axes3D(fig)
    pylab.rcParams['lines.markeredgewidth'] = 0

    min_size = 0
    max_size = 25
    color_code_axis = 5
    code = d[:, color_code_axis]
    norm = matplotlib.colors.Normalize(vmin=code.min(), vmax=code.max())
    m = matplotlib.cm.ScalarMappable(norm=norm, cmap=cm.jet)
    rgba_colors = m.to_rgba(code)
    marker_sizes = np.round(utils.transform_linear(code, (min_size, max_size)))
    p = ax.scatter(d[:, 0], d[:, 1], d[:, 2], c=np.array(rgba_colors), marker='o', linewidth='0', edgecolor=rgba_colors, s=marker_sizes)#, cmap='seismic')
    m.set_array(code)
    fig.colorbar(m)

    ax.set_xlabel('Stimulus position')
    ax.set_ylabel('Position after action')
    ax.set_zlabel('Stimulus speed')


def plot_rewards_for_one_speed(v_stim, n_pos=20):
    GP = simulation_parameters.global_parameters()
    params = GP.params
    BG = BasalGanglia.BasalGanglia(params, dummy=True)
    speeds = BG.action_bins_x

    x_pos = np.linspace(0., 1., n_pos)
    print 'x_pos:', x_pos

    stimuli_and_rewards = np.zeros((n_pos * 1 * params['n_actions'], 6))
    idx = 0
    for i_x in xrange(n_pos):
        x_old = x_pos[i_x]
        stim_params = [x_pos[i_x], .5, v_stim, 0.]
        for i_a in xrange(params['n_actions']):
            x_new = utils.get_next_stim(params, stim_params, speeds[i_a])[0]
            R = utils.get_reward_from_perceived_states(x_old, x_new)
            stimuli_and_rewards[idx, 0] = x_old
            stimuli_and_rewards[idx, 1] = x_new
            stimuli_and_rewards[idx, 2] = v_stim
            stimuli_and_rewards[idx, 3] = i_a
            stimuli_and_rewards[idx, 4] = speeds[i_a]
            stimuli_and_rewards[idx, 5] = R
            idx += 1


    print 'Rewards:', stimuli_and_rewards[:, 5]

    fig = pylab.figure()
    ax = Axes3D(fig)
    data = np.array([stimuli_and_rewards[:, 0], stimuli_and_rewards[:, 1], stimuli_and_rewards[:, 5]]).transpose()
    color_code_axis = 2
    code = data[:, color_code_axis]
    zlim = (code.min(), code.max()) # full range
#    zlim = (-2.5, 1.5)
    norm = matplotlib.colors.Normalize(vmin=zlim[0], vmax=zlim[1])
    m = matplotlib.cm.ScalarMappable(norm=norm, cmap=cm.jet)
    rgba_colors = m.to_rgba(code)
    min_size = 0
    max_size = 25
    marker_sizes = np.round(utils.transform_linear(code, (min_size, max_size)))
    p = ax.scatter(data[:, 0], data[:, 1], data[:, 2], c=np.array(rgba_colors), marker='o', linewidth='0', edgecolor=rgba_colors, s=15)#, s=marker_sizes)#, cmap='seismic')
#    p = ax.scatter(data[:, 0], data[:, 1], data[:, 2], c='k', marker='o', s=15)
    ax.set_xlabel('Stimulus position')
    ax.set_ylabel('Position after action')
    ax.set_zlabel('Reward')
    ax.set_zlim(zlim)

    # sort the x_new array
#    idx = np.lexsort((stimuli_and_rewards[:, 0], stimuli_and_rewards[:, 1], stimuli_and_rewards[:, 5]))
#    data = np.array([stimuli_and_rewards[idx, 0], stimuli_and_rewards[idx, 1], stimuli_and_rewards[idx, 5]]).transpose()
#    fig2 = pylab.figure()
#    ax = fig2.add_subplot(111)
#    cax = ax.pcolormesh(data, vmin=zlim[0], vmax=zlim[1])#, edgecolor='k', linewidths='1')
#    ax.set_ylim(0, data.shape[0])
#    ax.set_xlim(0, data.shape[1])
#    ax.set_xlabel('Stimulus position start')
#    ax.set_ylabel('Stimulus position after action')
#    fig2.colorbar(cax)

#    print 'axis 0', data[:, 0]
#    print 'axis 1', data[:, 1]
#    print 'axis 5', data[:, 2]


def plot_reward_vs_relative_improvement(n_v):
    """
    Plot the reward given for different actions derived from the 
    relative improvement 
    """
    pass


def plot_actions_and_rewards_for_single_stim(stim_params, ax=None, x_offset=0.):

    GP = simulation_parameters.global_parameters()
    params = GP.params
    BG = BasalGanglia.BasalGanglia(params, dummy=True)
    speeds = BG.action_bins_x
    x_old = stim_params[0]
    x_post = np.zeros(params['n_actions'])
    R = np.zeros(params['n_actions'])
    for i_a in xrange(params['n_actions']):
        x_new = utils.get_next_stim(params, stim_params, speeds[i_a])[0]
        R[i_a] = utils.get_reward_sigmoid(x_new, stim_params, params)
#        R[i_a] = utils.get_reward_gauss(x_new, stim_params, params)
#        R[i_a] = utils.get_reward_from_perceived_states(x_old, x_new)
        x_post[i_a] = x_new

    min_val = np.min(R)
    max_val = np.max(R)
    norm = matplotlib.colors.Normalize(vmin=min_val, vmax=max_val)
    cmap = matplotlib.cm.jet
    m = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    m.set_array(np.arange(min_val, max_val, 0.01))

    if ax == None:
        fig = pylab.figure(figsize=(18, 12))
        ax = fig.add_subplot(111)

    xa = 2.05
    for i_a in xrange(params['n_actions']):
        c_s = m.to_rgba(R[i_a])
        ax.plot([1. + x_offset, 2. + x_offset], [x_old, x_post[i_a]], c=c_s, lw=2)
        print 'R(%d, v_eye=%.2f)= %.2f' % (i_a, BG.action_bins_x[i_a], R[i_a])
        ypos_label = x_post[i_a]

    ax.text(x_offset - .1 + 1., stim_params[0] + .05, 'v=%.1f' % (stim_params[2]), color='k', fontsize=10)

#    for i_a in [0, 1, 2, 3, 4, 6, 8, 10, 12, 13, 14, 15, 16]:
    for i_a in [0, 1, 2, 3, 4, 9, 13, 14, 15, 16]:
#    for i_a in range(params['n_actions']):
        c_s = m.to_rgba(R[i_a])
        ypos_label = x_post[i_a]
        ax.text(xa + x_offset, ypos_label, 'R(%d, v_eye=%.2f)= %.2f' % (i_a, BG.action_bins_x[i_a], R[i_a]), color=c_s, fontsize=8)

    ax.set_xlim((0.9, 3.1 + x_offset))
    xlim = ax.get_xlim()
    ax.plot([xlim[0], xlim[1] + x_offset], [.5, .5], c='k', ls='--', lw=1)
    ax.set_title('Rewards for all actions, mp= (%.2f, %.2f)' % (stim_params[0], stim_params[2]))
    ax.set_ylabel('Retinal displacement')
    if ax == None:
        cbar = fig.colorbar(m)
        print 'setting colorbar'
    return ax


def plot_reward_schedule_gauss(params, x_pre_action, ls='-', ax=None, ax2=None):

    pylab.rcParams.update(plot_params)


    x_range_new = np.arange(0, 1., 0.01)
    v_range = np.arange(-2., 2., 0.4)
    R = np.zeros((len(x_range_new), len(v_range)))
    sigma_R = np.zeros((len(x_range_new), len(v_range)))
    for i_x in xrange(len(x_range_new)):
        for i_v in xrange(len(v_range)):
            stim_params = (x_pre_action, .5, v_range[i_v], .0)
            R[i_x, i_v], sigma_R[i_x, i_v] = utils.get_reward_gauss(x_range_new[i_x], stim_params, params)
            # _sigmaoid does not return a sigma value
#            debug = utils.get_reward_sigmoid(x_range_new[i_x], stim_params, params)
#            print 'DEBUG', debug
            R[i_x, i_v], sigma_R[i_x, i_v] = utils.get_reward_sigmoid(x_range_new[i_x], stim_params, params)

    n_curves = len(v_range)
    bounds = np.abs(v_range)
    bounds_sorted = np.sort(bounds)
    cmap = matplotlib.cm.jet
#    norm = matplotlib.colors.BoundaryNorm(bounds_sorted, cmap.N)
    norm = matplotlib.colors.Normalize(vmin=np.min(bounds), vmax=np.max(bounds))#, clip=True)
    m = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    m.set_array(np.arange(np.min(bounds), np.max(bounds), .1))
    rgba_colors = m.to_rgba(bounds)

    
    norm_x = matplotlib.colors.Normalize(vmin=0, vmax=0.5)
    m_x = matplotlib.cm.ScalarMappable(norm=norm_x, cmap=matplotlib.cm.jet)
    m_x.set_array(x_range_new)
    rgba_colors_x = m.to_rgba(x_range_new)

    fontsize = 20
    if ax == None:
        fig = pylab.figure(figsize=get_fig_size(1200))
        ax = fig.add_subplot(111)
        cb = fig.colorbar(m)
        cb.set_label('$|v_{stim}|$', fontsize=fontsize)

    if ax2 == None:
        fig2 = pylab.figure(figsize=get_fig_size(1200))
        ax_rx = fig2.add_subplot(211)
        cb_x = fig2.colorbar(m)
        cb_x.set_label('$|v_{stim}|$', fontsize=fontsize)

        ax_rv = fig2.add_subplot(212)
        cb_x = fig2.colorbar(m_x)
        cb_x.set_label('$|x_{stim} - x_{post}|$', fontsize=fontsize)


    for i_v in xrange(len(v_range)):
        p, = ax.plot(x_range_new, R[:, i_v], color=rgba_colors[i_v], lw=2, ls=ls)
        ax_rx.plot(x_range_new, sigma_R[:, i_v], color=rgba_colors[i_v], lw=2, ls=ls) 
    ax_rx.set_title('$x_{stim}$ before action = %.2f' % x_pre_action)
    ax_rx.set_xlabel('x post')
    ax_rx.set_ylabel('$\sigma_{R}$')

    for i_x in xrange(len(x_range_new)):
#        ax_rv.plot(v_range, sigma_R[i_x, :], lw=2, ls=ls) 
        ax_rv.plot(v_range, sigma_R[i_x, :], color=rgba_colors_x[i_x], lw=2, ls=ls) 
    ax_rv.set_xlabel('v_stim')
    ax_rv.set_ylabel('$\sigma_{R}$')

    ax.set_xlabel('$x_{stim}$ after action', fontsize=fontsize)
    ax.set_ylabel('Rewards', fontsize=fontsize)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xlim_mid = .5 * (xlim[1] - xlim[0]) + xlim[0]
    ax.plot((xlim_mid, xlim_mid), (ylim[0], ylim[1]), c='k', ls='-', lw=5)
    ax.plot((xlim[0], xlim[1]), (0., 0.), c='k', ls='-', lw=5)

    p, = ax.plot((x_pre_action, x_pre_action), (ylim[0], ylim[1]), ls=ls, c='k', lw=2)

    return ax, p


def plot_reward_schedule_single_actions(params, x_pre_action, n_speeds, v_max=1., ls='-', ax=None):

    BG = BasalGanglia.BasalGanglia(params, dummy=True)
    actions_v = BG.action_bins_x

    stim_speeds = np.linspace(-v_max, v_max, n_speeds)
    lw_max = 8
    lw_min = 1
    line_widths = utils.transform_linear(stim_speeds, (lw_min, lw_max))

    x_post_action = np.zeros((n_speeds, params['n_actions']))
    R = np.zeros((n_speeds, params['n_actions']))
    for i_v, v_stim in enumerate(stim_speeds):
        for i_ in xrange(params['n_actions']):
            stim_params = (x_pre_action, .5, v_stim, .0)
            x_post_action[i_v, i_] = utils.get_next_stim(params, stim_params, actions_v[i_])[0]
#            R[i_v, i_], sigma_r = utils.get_reward_gauss(x_post_action[i_v, i_], stim_params, params)
            R[i_v, i_], sigma_r = utils.get_reward_sigmoid(x_new, stim_params, params)

#    bounds = np.abs(actions_v)
    if n_speeds > 1:
        bounds = np.array(stim_speeds)
        cmap = matplotlib.cm.jet
        norm = matplotlib.colors.Normalize(vmin=np.min(bounds), vmax=np.max(bounds))#, clip=True)
        m = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
        m.set_array(np.arange(np.min(bounds), np.max(bounds), .1))
        rgba_colors = m.to_rgba(bounds)

    fontsize = 20
    if ax == None:
        fig = pylab.figure(figsize=get_fig_size(1200))
        ax = fig.add_subplot(111)
        if n_speeds > 1:
            cb = fig.colorbar(m)
            cb.set_label('$|v_{stim}|$', fontsize=fontsize)


    for i_v, v_stim in enumerate(stim_speeds):
#        lw = line_widths[i_v]
        lw = 2
        for i_ in xrange(params['n_actions']):
            if n_speeds > 1:
                p, = ax.plot((x_pre_action, x_post_action[i_v, i_]), (0., R[i_v, i_]), ls=ls, color=rgba_colors[i_v], lw=lw)
            else:
                p, = ax.plot((x_pre_action, x_post_action[i_v, i_]), (0., R[i_v, i_]), ls=ls, color='b', lw=lw)

    ax.set_xlabel('$x_{stim}$ before and after action', fontsize=fontsize)
    ax.set_ylabel('Rewards', fontsize=fontsize)
    ax.set_xlim((0., 1.))
    ax.set_ylim((params['neg_kappa'], params['pos_kappa']))
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xlim_mid = .5 * (xlim[1] - xlim[0]) + xlim[0]
    ax.plot((xlim_mid, xlim_mid), (ylim[0], ylim[1]), c='k', ls='-', lw=5)
    ax.plot((xlim[0], xlim[1]), (0., 0.), c='k', ls='-', lw=5)

#    p, = ax.plot((x_pre_action, x_pre_action), (ylim[0], ylim[1]), ls=ls, c='k', lw=3)

    return ax, p


if __name__ == '__main__':

#    test_random_placements()
#    all_data = get_rewards_for_all_stimuli_and_actions(n_pos=50, n_v=5)
#    plot_4d(all_data)  
#    v_stim = 1.0
#    plot_rewards_for_one_speed(v_stim, n_pos=100)

    GP = simulation_parameters.global_parameters()
    params = GP.params

    x_pre_actions = [0.05, 0.49]
#    x_pre_actions = [0.05, 0.1, 0.2, 0.3, 0.4, 0.49]
    linestyles = ['-', '-.', '--', ':', '-', '-.']
    plots = []
    labels = []
    ax = None
    plots2 = []
    labels2 = []
    ax2 = None
    ax_r = None
    stim_speeds = [.1]#, 0.5, 1.0]
    n_speeds = 1
    v_max = 2.0
    for i_, x_pre_action in enumerate(x_pre_actions):
#        ax, p = plot_reward_schedule_gauss(params, x_pre_action, ls=linestyles[i_], ax=ax, ax2=ax_r)
#        label = '$x_{stim}$ before action: %.2f' % (x_pre_action)
#        labels.append(label)
#        plots.append(p)

#        for i_v, v_stim in enumerate(stim_speeds):
#        ax2, p2 = plot_reward_schedule_single_actions(params, x_pre_action, n_speeds, v_max=v_max, ax=ax2)
        ax2, p2 = plot_reward_schedule_single_actions(params, x_pre_action, n_speeds, v_max=v_max, ls=linestyles[i_], ax=ax2)

#        label2 = '$v_{stim}$ : %.2f' % (v_stim)
#        labels2.append(label2)
#        plots2.append(p2)


    ax.legend(plots, labels)
#    ax2.legend(plots2, labels2)


    # plot some examples 
#    motion_params = [(.9, .5, -2., 0.), \
#                    (.5, .5, .2, 0.), \
#                    (.1, .5, -2., 0.), \
#                    (.45, .5, .2, 0.), \
#                    (.45, .5, -2., 0.)]
#    ax = None
#    for i_, mp in enumerate(motion_params):
#        ax = plot_actions_and_rewards_for_single_stim(mp, ax=ax, x_offset=1.2 * i_)

    pylab.show()

    #    print '%2d\t%.2f\t%.2f\t%.2f\t%.2f' % (i_, x[i_], dx[i_], dx_abs[i_], dj_di_abs[i_])
