#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides highpass-filtered timeseries."""

import scipy.signal as sg
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax0, ax1) = apl.subplots_mm(
        figsize=(180, 90), ncols=2, sharey=True, gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=12.5))

    # prepare filter (order, cutoff)
    filt = sg.butter(2, 3/24.0, 'high')

    # for each tilt unit
    pres = util.tid.load_inc('wlev')
    for i, unit in enumerate(pres):

        # crop, resample, and interpolate
        series = pres[unit].dropna().resample('1H').mean().interpolate()  # kPa

        # apply filter in both directions
        series[:] = sg.filtfilt(*filt, series) + 5.0*(8-i)

        # plot
        for ax in (ax0, ax1):
            series.plot(ax=ax)

    # plot tide data
    z = util.tid.load_pituffik_tides().resample('1H').mean() - 20.0  # kPa
    for ax in (ax0, ax1):
        z.plot(ax=ax, c='k', label='Tide')

    # set axes properties
    ax0.set_ylim(-35.0, 45.0)
    ax0.set_ylabel('pressure anomaly (kPa)')
    ax0.legend(ncol=2, loc='center right')  # bbox_to_anchor=(1.0, 0.15))

    # zooming windows  # FIXME formalise presentation mode
    zooms = dict(
        z1=['20140901', '20141001'],  # zoom with all sensors, L3 not frozen
        z2=['20140910', '20140915'],  # zoom on phase, L3 not frozen
        z3=['20141120', '20141125'],  # zoom phase, U2 and U2 lost
        z4=['20150101', '20150201'],  # zoom on 14-day modulation, 2 cycles
        z5=['20150901', '20151101'],  # zoom on 14-day modulation, 4 cycles
        z6=['20150601', '20150715'])  # zoom on summer, more complicated

    # save without right panel
    # ax1.set_visible(False)
    # fig.savefig(__file__[:-3]+'_z0')
    # ax1.set_visible(True)

    # mark zoom inset
    mark_inset(ax0, ax1, loc1=2, loc2=3, ec='0.5', ls='--')

    # save different zooms
    # for k, v in zooms.iteritems():
    #     grid[1].set_xlim(*v)
    #     fig.savefig(__file__[:-3]+'_'+k)

    # save default
    ax1.set_xlim(*zooms['z1'])
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
