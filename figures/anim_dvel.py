#!/usr/bin/env python2

import util as ut
import pandas as pd
from matplotlib.animation import FuncAnimation

# dates to plot
start = '2014-11-01'
end = '2015-12-01'

# load data
exz = {bh: ut.io.load_strain_rate(bh, '1D')[start:end] for bh in ut.boreholes}
depth = {bh: ut.io.load_depth('tiltunit', bh).squeeze() for bh in ut.boreholes}
depth_base = {bh: ut.io.load_depth('pressure', bh).squeeze() for bh in ut.boreholes}

# ignore two lowest units on upstream borehole
broken = ['unit02', 'unit03']
depth['upstream'].drop(broken, inplace=True)
exz['upstream'].drop(broken, axis='columns', inplace=True)

# concatenate
exz = pd.concat(exz, axis='columns', keys=ut.boreholes)
depth = pd.concat(depth)
depth_base = pd.Series(depth_base)

# drawing function for animation
def draw(date, fig, grid, xlabel):

    # get date string
    datestring = date.strftime('%Y-%m-%d')
    print 'plotting frame at %s ...' % datestring

    # update xlabel
    xlabel.set_text('ice deformation on %s ($m\,a^{-1}$)' % datestring)

    # loop over boreholes
    for j, bh in enumerate(ut.boreholes):
        ax = grid[j]
        ax.cla()
        c = ut.colors[j]

        # plot velocity profile
        ut.pl.plot_vsia_profile(depth[bh], exz[bh].loc[datestring],
                                depth_base[bh], ax=ax, c=c)

        # set axes limits
        ax.set_ylim(300.0, 0.0)
        ax.set_xlim(50.0, 0.0)

    # remove right axis tick labels
    for label in ax.get_yticklabels():
        label.set_visible(False)

# initialize figure and labels
fig, grid = ut.pl.subplots_mm(nrows=1, ncols=2, sharex=True, sharey=True,
                             left=10.0, bottom=10.0, right=5.0, top=5.0,
                             wspace=5.0, hspace=5.0)
figw, figh = fig.get_size_inches()*25.4
xlabel = fig.text(0.5, 2.5/figh, '', ha='center')
ylabel = fig.text(2.5/figw, 0.5, 'depth (m)', va='center', rotation='vertical')

# create animation
anim = FuncAnimation(fig, draw, frames=exz.index,
                     fargs=(fig, grid, xlabel))

# save
anim.save('anim_dvel.mp4', fps=25, dpi=254, bitrate=1024)
