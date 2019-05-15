#!/usr/bin/env python

import util as ut


# dates to plot
dates = dict(
    bh1=['2014-10-25', '2015-10-14', '2017-01-28'],
    bh2=['2014-11-01', '2015-07-14'],
    bh3=['2015-01-01', '2015-04-01', '2015-07-12', '2015-11-12', '2016-06-19'])

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=1, ncols=1,
                            sharex=False, sharey=True, wspace=2.5,
                            left=10.0, right=2.5, bottom=10.0, top=2.5)

# loop on boreholes
for bh, c in zip(ut.bowtem_bhnames, ut.bowtem_colours):

    # load data
    t, z, b = ut.io.load_bowtem_data(bh)

    # plot first date
    d0 = dates[bh][0]
    t0 = t[d0].mean()
    ax.plot(t0, z, c=c, label='%s, %s' % (bh.upper(), d0))
    for s, m in zip(ut.bowtem_sensors, ut.bowtem_markers):
        cols = z.index.str[1] == s
        if cols.sum() > 0:
            ax.plot(t0[cols], z[cols], c=c, marker=m, ls='', label='')

    # plot next dates
    for d in dates[bh][1:]:
        ax.plot(t[d].mean(), z, c=c, ls='--', label='')

    # add base line
    ax.axhline(b, c=c, lw=0.5)

# plot melting point
b = 272.0       # base
g = 9.80665     # gravity
rhoi = 910.0    # ice density
beta = 7.9e-8   # Luethi et al. (2002)
melt = -beta * rhoi * g * b
ax.plot([0.0, melt], [0.0, b], c='k', ls=':')

# set axes properties
ax.legend(loc='lower left')
ax.set_xlabel(u'ice temperature (°C)')
ax.set_ylabel('initial depth (m)')
ax.axhline(0.0, c='k', lw=0.5)
ax.invert_yaxis()

# save
ut.pl.savefig(fig)
