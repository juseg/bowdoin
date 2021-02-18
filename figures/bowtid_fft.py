#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import util
import numpy as np
import absplots as apl


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(figsize=(180, 90), nrows=3, ncols=4,
        sharex=True, sharey=True, gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, hspace=2.5, wspace=2.5))

    # get freezing dates
    t = util.tid.load_inc('temp')['20140717':].resample('1H').mean()
    df = abs(t-(0.1*t.max()+0.9*t.min())).idxmin()  # date of freezing

    # for each tilt unit
    p = util.tid.load_inc('wlev')['2014-07':]
    for i, u in enumerate(p):
        ax = grid.T.flat[i]
        c = 'C%d' % i

        # crop and resample
        ts = p[u][df[u]:].dropna().resample('1H').mean().interpolate().diff()[1:]/3.6

        # only nulls, add text
        if ts.notnull().sum() == 0:
            ax.set_xlim(grid.flat[0].get_xlim())  # avoid reshape axes
            ax.set_ylim(grid.flat[0].get_ylim())  # avoid reshape axes
            ax.text(0.5, 0.5, 'no data', color='0.5', ha='center', transform=ax.transAxes)

        # else compute fft
        else:
            freq = np.fft.rfftfreq(ts.shape[-1], 1.0)
            rfft = np.fft.rfft(ts.values)
            ampl = np.abs(rfft)
            spow = ampl**2
            gain = 10.0*np.log10(spow)

            # and plot
            ax.plot(1/freq[1:], spow[1:], c=c)  # freq[0]=0.0
            ax.set_xscale('log')
            ax.set_yscale('log')

            # add vertical lines
            for x in [12.0, 12.0*30/29, 24.0, 24.0*14]:
                ax.axvline(x, c='0.75', lw=0.1, zorder=1)

        # add corner tag
        ax.text(0.95, 0.1, u, color=c, ha='right', transform=ax.transAxes)

    # plot tide data
    tide = util.tid.load_pituffik_tides().resample('1H').mean()
    tide = tide.interpolate().diff()[1:]/3.6
    freq = np.fft.rfftfreq(tide.shape[-1], 1.0)
    rfft = np.fft.rfft(tide.values)
    ampl = np.abs(rfft)
    spow = ampl**2
    gain = 10.0*np.log10(spow)
    for x in [12.0, 12.0*30/29, 24.0, 24.0*14]:
        ax.axvline(x, c='0.75', lw=0.1, zorder=1)
    grid[1, 3].plot(1/freq[1:], spow[1:], c='k')  # freq[0]=0.0
    grid[1, 3].text(0.95, 0.1, 'Tide', color='k', ha='right',
                    transform=grid[1, 3].transAxes)

    # set axes properties
    grid[2, 1].set_xlabel('period (h)')
    grid[1, 0].set_ylabel(r'spectral power ($Pa^2 s^{-2}$)', labelpad=0)

    # remove unused axes
    grid[0, 3].set_visible(False)
    grid[2, 3].set_visible(False)

    # save
    fig.savefig(__file__[:-3])

    ## save different zooms
    #fig.savefig(__file__[:-3]+'_z0')
    #ax.set_xscale('linear')
    #ax.set_xticks([12.0, 24.0])
    #ax.set_xlim(6.0, 30.0)
    #fig.savefig(__file__[:-3]+'_z1')
    #ax.set_xticks([12.0, 12.0*30/29])
    #ax.set_xlim(11.5, 13.0)
    #fig.savefig(__file__[:-3]+'_z2')


if __name__ == '__main__':
    main()
