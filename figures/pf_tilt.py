#!/usr/bin/env python2

import util as ut

# dates to plot
start = '2014-11-01'
end = '2015-07-01'

# initialize figure
fig, grid = ut.pl.subplots_mm(nrows=1, ncols=2, sharex=True, sharey=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[i]

    # read data values
    depth = ut.io.load_depth('tiltunit', bh).squeeze()
    depth_base = ut.io.load_depth('pressure', bh).squeeze()
    exz = ut.io.load_total_strain(bh, start, end)

    # remove null values
    notnull = exz.notnull()
    depth = depth[notnull]
    exz = exz[notnull]

    # plot velocity profile
    ut.pl.plot_vsia_profile(depth, exz, depth_base, ax=ax, c=c)

    # set axes properties
    ax.set_title(bh)

# set axes properties
ax.set_ylim(300.0, 0.0)
ax.set_xlim(25.0, 0.0)

# add common labels
figw, figh = fig.get_size_inches()*25.4
xlabel = 'total ice deformation from %s to %s (m)' % (start, end)
fig.text(0.5, 2.5/figh, xlabel, ha='center')
fig.text(2.5/figw, 0.5, 'depth (m)', va='center', rotation='vertical')

# save
fig.savefig('pf_tilt')
