#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress derivative time series."""

from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import absplots as apl
import bowtem_utils
import bowstr_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax0, ax1) = apl.subplots_mm(
        figsize=(180, 90), ncols=2, sharey=True, gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=7.5))

    # add subfigure labels
    bowtem_utils.add_subfig_labels((ax0, ax1))

    # plot tilt unit water level
    pres = bowstr_utils.load().resample('1h').mean()
    pres = pres.diff()[1:]/3.6 + 9 - range(pres.shape[1])  # Pa s-1
    pres.plot(ax=ax0)
    pres.plot(ax=ax1, legend=False)

    # plot tide data
    tide = bowstr_utils.load_pituffik_tides().resample('1h').mean()
    tide = tide.diff()[1:]/3.6  # Pa s-1
    tide.plot(ax=ax1, c='k', label='Tide')

    # set axes properties
    ax0.set_ylim(-1.0, 10.0)
    ax0.set_ylabel(r'stress change ($Pa\,s^{-1}$)')
    ax0.legend(ncol=2, loc='lower right')

    # zooming windows
    zooms = dict(
        z1=['20140901', '20141001'],  # zoom with all sensors, L3 not frozen
        z2=['20140910', '20140915'],  # zoom on phase, L3 not frozen
        z3=['20141120', '20141125'],  # zoom phase, U2 and U2 lost
        z4=['20150101', '20150201'],  # zoom on 14-day modulation, 2 cycles
        z5=['20150901', '20151101'],  # zoom on 14-day modulation, 4 cycles
        z6=['20150601', '20150715'])  # zoom on summer, more complicated

    # save without right panel  # FIXME formatlise presentation mode
    # grid[1].set_visible(False)
    # fig.savefig(__file__[:-3]+'_z0')
    # grid[1].set_visible(True)

    # mark zoom inset
    mark_inset(ax0, ax1, loc1=2, loc2=3, ec='0.5', ls='--')

    # save different zooms
    # for k, v in zooms.iteritems():
    #     grid[1].set_xlim(*v[:2])
    #     grid[1].set_ylim(*v[2:])
    #     fig.savefig(__file__[:-3]+'_'+k)

    # save default
    ax1.set_xlim(*zooms['z1'])
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
