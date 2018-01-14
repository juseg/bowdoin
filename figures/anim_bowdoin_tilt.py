#!/usr/bin/env python2

import util as ut
import pandas as pd
from matplotlib.animation import FuncAnimation

# dates to plot
start = '2014-11-01'
end = '2015-11-01'

# load data
exz = {bh: ut.io.load_total_strain(bh, start)[start:end] for bh in ut.boreholes}
depth = {bh: ut.io.load_depth('tiltunit', bh).squeeze() for bh in ut.boreholes}
depth_base = {bh: ut.io.load_depth('pressure', bh).squeeze() for bh in ut.boreholes}

# ignore two lowest units on upper borehole
broken = ['unit02', 'unit03']
depth['upper'].drop(broken, inplace=True)
exz['upper'].drop(broken, axis='columns', inplace=True)

# concatenate and resample
exz = pd.concat(exz, axis='columns', keys=ut.boreholes)
exz = exz.resample('1D').mean()
depth = pd.concat(depth)
depth_base = pd.Series(depth_base)

# drawing function for animation
def draw(date, fig, grid, cursor):

    # get date string
    datestring = date.strftime('%Y-%m-%d')
    print 'plotting frame at %s ...' % datestring

    # loop over boreholes
    for j, bh in enumerate(ut.boreholes):
        ax = grid[j]
        ax.cla()
        c = ut.colors[bh]

        # plot velocity profile
        ut.pl.plot_vsia_profile(depth[bh], exz[bh].loc[datestring],
                                depth_base[bh], ax=ax, c=c)

        # set axes limits and labels
        ax.set_ylim(300.0, 0.0)
        ax.set_xlim(35.0, 0.0)
        ax.set_title(bh)
        ax.set_ylabel('depth (m)')

    # remove right axis tick labels
    for label in ax.get_yticklabels():
        label.set_visible(False)

    # update cursor
    cursor.set_data(date, (0.0, 1.0))

# initialize figure and labels
figw, figh = 135.0, 120.0
fig, grid = ut.pl.subplots_mm(nrows=1, ncols=2, figsize=(figw, figh),
                              left=10.0, bottom=45.0, right=2.5, top=5.0,
                              wspace=5.0, hspace=5.0, sharex=True, sharey=True)
tsax = fig.add_axes([10.0/figw, 10.0/figh, 1-12.5/figw, 30.0/figh])

# plot time series
for i, bh in enumerate(ut.boreholes):
    c = ut.colors[bh]

    # fit to a Glen's law
    n, A = ut.al.glenfit(depth[bh], exz[bh].T)

    # calc deformation velocity
    vdef = ut.al.vsia(0.0, depth_base[bh], n, A)
    vdef = pd.Series(index=exz.index, data=vdef)
    vdef = vdef.diff()*100.0

    # plot
    vdef.plot(ax=tsax, c=c, label=bh)

# add cursor
cursor = tsax.axvline(0.0, c='k', lw=0.25)

# set labels
tsax.set_ylabel(r'deformation velocity ($cm\,day^{-1}$)')
tsax.set_xlim(start, end)
tsax.set_ylim(5.0, 15.0)
tsax.legend()

# add signature
fig.text(1-2.5/figw, 2.5/figh, 'J. Seguinot et al. (2016)',
         ha='right', va='bottom')

# create animation
anim = FuncAnimation(fig, draw, frames=exz.index, fargs=(fig, grid, cursor))

# save
anim.save('anim_bowdoin_tilt.mp4', fps=25, codec='h264')
anim.save('anim_bowdoin_tilt.ogg', fps=25, codec='theora')
