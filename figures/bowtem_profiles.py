#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature profiles."""

import absplots as apl
import util


def main():
    """Main program called during execution."""

    # dates to plot
    # FIXME store these dates in utils and plot
    dates = dict(
        bh1=['2014-10-25', '2015-10-14', '2017-01-28'],
        bh2=['2014-11-01', '2015-07-14'],
        bh3=['2015-01-01', '2015-04-01', '2015-07-12', '2015-11-12',
             '2016-06-19'],
        err=['2015-01-01', '2015-04-01', '2015-07-12', '2015-11-12',
             '2016-06-19'])

    # initialize figure
    gridspec_kw = dict(left=10, right=2.5, wspace=2.5, bottom=10, top=2.5)
    fig, (ax0, ax1) = apl.subplots_mm(figsize=(150, 75), ncols=2, sharey=True,
                                      gridspec_kw=gridspec_kw)

    # add subfigure labels
    util.com.add_subfig_label(ax=ax0, text='(a)', ypad=15)
    util.com.add_subfig_label(ax=ax1, text='(b)', ypad=15)

    # for each borehole
    for bh, color in util.tem.COLOURS.items():

        # load all data
        temp, depth, base = util.tem.load_all(bh)

        # plot initial profiles
        date0 = dates[bh][0]
        temp0 = temp[date0].mean()
        ax0.plot(temp0, depth, c=color, label='%s, %s' % (bh.upper(), date0))

        # add markers
        for sensor, marker in util.tem.MARKERS.items():
            cols = depth.index.str[1] == sensor
            if cols.sum() > 0:
                ax0.plot(temp0[cols], depth[cols], c=color, marker=marker,
                         ls='', label='')

        # plot next profiles
        for date1 in dates[bh][1:]:
            temp1 = temp[date1].mean()
            ax0.plot(temp1, depth, c=color, ls='--', lw=0.5, label='')
            ax1.plot(temp1-temp0, depth, c=color, ls='--', lw=0.5, label='')

        # add base line
        for ax in (ax0, ax1):
            ax.axhline(base, color=color, lw=0.5)

    # add ice surface
    for ax in (ax0, ax1):
        ax.axhline(0, color='k', lw=0.5)

    # plot melting point and zero line
    # FIXME move ice physical parameters somewhere
    base = 272.0    # glacier base
    gravity = 9.80665     # gravity
    rhoi = 910.0    # ice density
    beta = 7.9e-8   # Luethi et al. (2002)
    melt = -beta * rhoi * gravity * base
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
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
