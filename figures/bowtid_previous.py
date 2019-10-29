#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import util
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import absplots as apl


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(figsize=(180, 90), ncols=2, sharey=True,
        gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=12.5))

    # Temperature profiles
    # --------------------

    ax = grid[0]
    colors = dict(upper='C0', lower='C6')

    # dates to plot
    dates = dict(upper=['2015-01-01', '2016-07-12'],
                 lower=['2015-01-01', '2015-11-12', '2016-07-19'])
    styles = ['-', ':', ':']

    # markers per sensor type
    markers = dict(temp='o', unit='^')  #, pres='s')

    # for each borehole
    base_depth = 0.0
    for i, bh in enumerate(ut.boreholes):
        c = colors[bh]

        # read temperature and depth data
        temp_depth = ut.io.load_depth('thstring', bh)
        tilt_depth = ut.io.load_depth('tiltunit', bh)
        pres_depth = ut.io.load_depth('pressure', bh)
        pres_depth.index = ['pres']
        manu_temp = ut.io.load_data('thstring', 'mantemp', bh)
        temp_temp = ut.io.load_data('thstring', 'temp', bh)
        tilt_temp = ut.io.load_data('tiltunit', 'temp', bh)

        # prepare depth profile
        depth = pd.concat((temp_depth, tilt_depth))
        subglac = depth > 0.0
        notnull = depth.notnull() #& temp.notnull()
        depth = depth[notnull&subglac].sort_values()

        # for each date to plot
        for date, ls in zip(dates[bh], styles):

            # prepare combined profiles
            if date in temp_temp.index:
                temp = temp_temp[date].mean()
            else:
                temp = manu_temp[date].squeeze()
            if date in tilt_temp.index:
                temp = temp.append(tilt_temp[date].mean())

            # order by depth, remove nulls and sensors above ground
            temp = temp[depth.index.values]

            # plot profiles
            label = '{}, {}'.format(bh, date)
            ax.plot(temp, depth, c=c, ls=ls, label=label)
            if date == dates[bh][0]:
                for sensor, marker in list(markers.items()):
                    cols = [s for s in temp.index if s.startswith(sensor)]
                    ax.plot(temp[cols], depth[cols], marker, c=c)

        # add base line  # FIXME UI02 is lower than that
        #ax.plot([temp['temp01']-0.5, temp['temp01']+0.5],
        #        [depth['temp01'], depth['temp01']], c='k')

        # compute maximum depth
        base_depth = max(base_depth, pres_depth.squeeze())

    # plot melting point
    g = 9.80665     # gravity
    rhoi = 910.0    # ice density
    beta = 7.9e-8   # Luethi et al. (2002)
    base_temp_melt = -beta * rhoi * g * base_depth
    ax.plot([0.0, base_temp_melt], [0.0, base_depth], c='k', ls=':')

    # set axes properties
    ax.invert_yaxis()
    ax.set_xlabel('ice temperature (°C)')
    ax.set_ylabel('depth (m)')
    ax.legend(loc='lower left')

    # Deformation profile
    # -------------------

    ax = grid[1]
    bh = 'upper'
    c = colors[bh]

    # dates to plot
    start = '2014-11'
    end = '2016-11'

    # read data values
    depth = ut.io.load_depth('tiltunit', bh).squeeze()
    base = depth.max()
    exz = ut.io.load_total_strain(bh, start, end)

    # remove null values
    notnull = exz.notnull()
    depth = depth[notnull]
    exz = exz[notnull]/2.0

    # plot velocity profile
    ut.pl.plot_vsia_profile(depth, exz, base, ax=ax, c=c)
    grid[0].axhline(base)

    # set axes properties
    ax.set_ylim(300.0, 0.0)
    ax.set_xlim(35.0, 0.0)

    # add common labels
    ax.set_xlabel(r'ice deformation %s to %s ($m\,a^{-1}$)' % (start, end))

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
