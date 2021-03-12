#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import util
import numpy as np
import scipy.signal as sg
import absplots as apl


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(figsize=(180, 90), nrows=3, ncols=3,
        sharex=True, sharey=True, gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, hspace=2.5, wspace=12.5))

    # for each tilt unit
    p = util.str.load_inc('wlev')['2014-11':].diff()[1:]
    for i, u in enumerate(p):
        ax = grid.flat[i]
        c = 'C%d' % i

        # crop
        ts = p[u].dropna()

        # only nulls, add text
        if ts.notnull().sum() == 0:
            ax.set_xlim(grid.flat[0].get_xlim())  # avoid reshape axes
            ax.set_ylim(grid.flat[0].get_ylim())  # avoid reshape axes
            ax.text(0.5, 0.5, 'no data', color='0.5', ha='center', transform=ax.transAxes)

        # else compute fft
        else:
            x = (ts.index - ts.index[0]).total_seconds()/3600
            y = ts.values
            periods = np.linspace(6.0, 30.0, 1001)
            frequencies = 1.0 / periods
            angfreqs = 2 * np.pi * frequencies
            pgram = sg.lombscargle(x, y, angfreqs, normalize=False)

            # and plot
            ax.plot(periods, pgram, c=c)  # freq[0]=0.0
            ax.set_xticks([12.0, 24.0])
            ax.set_yscale('log')

            # add vertical lines
            for x in [12.0, 12.0*30/29, 24.0]:
                ax.axvline(x, c='0.75', lw=0.1, zorder=1)

        # add corner tag
        ax.text(0.9, 0.1, u, color=c, transform=ax.transAxes)

    # set axes properties
    grid[2, 1].set_xlabel('period (h)')
    grid[1, 0].set_ylabel(r'spectral power ($Pa^2 s^{-2}$)', labelpad=0)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
