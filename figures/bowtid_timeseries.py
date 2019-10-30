#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides pressure time series."""

from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax0, ax1) = apl.subplots_mm(
        figsize=(180, 90), ncols=2, gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=12.5))

    # plot tilt unit water level
    pres = util.tid.load_inc('wlev').resample('1H').mean()/1e3
    pres.plot(ax=ax0, legend=True, x_compat=True)
    pres.plot(ax=ax1, legend=False, x_compat=True)

    # plot freezing dates
    temp = util.tid.load_inc('temp')['20140717':].resample('1H').mean()
    date = abs(temp-(0.1*temp.max()+0.9*temp.min())).idxmin()
    for ax in (ax0, ax1):
        ax.plot(date, [pres.loc[date[k], k] for k in date.index], 'k+')

    # add labels
    ax0.set_ylabel('pressure (MPa)')
    ax0.legend(loc='upper right', ncol=3)

    # zooming windows
    zooms = dict(
        z1=['20140715', '20141015', 0.25, 3.85],  # zoom on closure phase
        z2=['20140901', '20141001', 1.15, 1.55],  # 12-h cycle U5, U4, U3, L4
        z3=['20150101', '20150201', 1.55, 1.80],  # 12-h cycle U5, U4
        z4=['20150901', '20151015', 1.55, 1.65],  # 12-h cycle U5
        z5=['20150915', '20151115', 2.00, 2.30],  # 14-day mode U4, L3
        z6=['20170315', '20170501', 1.35, 1.45],)  # 14-day mode U5

    # save without right panel  # FIXME formalise presentation mode
    # ax1.set_visible(False)
    # util.com.savefig(fig, suffix='_z0')
    # ax1.set_visible(True)

    # mark zoom inset
    mark_inset(ax0, ax1, loc1=2, loc2=3, ec='0.5', ls='--')

    # save different zooms
    # for k, v in zooms.iteritems():
    #     grid[1].set_xlim(*v[:2])
    #     grid[1].set_ylim(*v[2:])
    #     util.com.savefig(fig, suffix='_'+k)

    # save default
    ax1.set_xlim(*zooms['z2'][:2])
    ax1.set_ylim(*zooms['z2'][2:])
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
