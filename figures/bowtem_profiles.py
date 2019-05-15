#!/usr/bin/env python

import absplots as apl
import util as ut


# dates to plot
dates = dict(
    bh1=['2014-10-25', '2015-10-14', '2017-01-28'],
    bh2=['2014-11-01', '2015-07-14'],
    bh3=['2015-01-01', '2015-04-01', '2015-07-12', '2015-11-12', '2016-06-19'])

# initialize figure
fig, (ax0, ax1) = apl.subplots_mm(figsize=(150, 75), ncols=2, sharey=True,
                                  gridspec_kw=dict(left=10, right=2.5,
                                                   bottom=10, top=2.5,
                                                   wspace=2.5))

# add subfigure labels
ut.pl.add_subfig_label(ax=ax0, text='(a)', y=0.95)
ut.pl.add_subfig_label(ax=ax1, text='(b)', y=0.95)

# for each borehole
for bh, c in zip(ut.bowtem_bhnames, ut.bowtem_colours):

    # load data
    t, z, b = ut.io.load_bowtem_data(bh)

    # plot initial profiles
    d0 = dates[bh][0]
    t0 = t[d0].mean()
    ax0.plot(t0, z, c=c, label='%s, %s' % (bh.upper(), d0))

    # add markers
    for s, m in zip(ut.bowtem_sensors, ut.bowtem_markers):
        cols = z.index.str[1] == s
        if cols.sum() > 0:
            ax0.plot(t0[cols], z[cols], c=c, marker=m, ls='', label='')

    # plot next profiles
    for d in dates[bh][1:]:
        t1 = t[d].mean()
        ax0.plot(t1, z, c=c, ls='--', lw=0.5, label='')
        ax1.plot(t1-t0, z, c=c, ls='--', lw=0.5, label='')

    # add base line
    for ax in (ax0, ax1):
        ax.axhline(b, c=c, lw=0.5)

# add ice surface
for ax in (ax0, ax1):
    ax.axhline(0.0, c='k', lw=0.5)

# plot melting point and zero line
base = 272.0    # glacier base
g = 9.80665     # gravity
rhoi = 910.0    # ice density
beta = 7.9e-8   # Luethi et al. (2002)
melt = -beta * rhoi * g * base
ax0.plot([0, melt], [0, base], c='k', ls=':', lw=0.5)
ax1.plot([0, 0], [0, base], c='k', ls=':', lw=0.5)

# set axes properties
ax0.invert_yaxis()
ax0.legend(loc='lower left')
ax0.set_ylabel('initial sensor depth (m)')
ax0.set_xlabel(u'ice temperature (°C)')
ax1.set_xlabel(u'temperature change (°C)')
ax1.set_xlim(-0.3, 0.7)

# save
ut.pl.savefig(fig)
