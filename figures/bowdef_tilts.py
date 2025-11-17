#!/usr/bin/env python
# Copyright (c) 2015-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress filtered line plots."""

import absplots as apl
import matplotlib as mpl
import numpy as np

import bowstr_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
            'left': 15, 'right': 2.5, 'bottom': 10, 'top': 2.5})
    inset = fig.add_axes_mm([17.5, 50, 35, 35])

    # plot tilt angular distance
    tilx = bowstr_utils.load(variable='tilx')
    tily = bowstr_utils.load(variable='tily')
    tilx = tilx[tilx.index >= '2014-07-17']
    tily = tily[tily.index >= '2014-07-17']
    tilt = np.arccos(np.cos(tilx)*np.cos(tily)) * 180 / np.pi
    tilt.plot(ax=ax, xlabel='', ylabel='tilt angular distance (°)')

    # set axes properties
    ax.set_xlim('2014-07-01', '2017-08-01')
    ax.legend(loc='lower right', ncols=3)

    # format date axis (FIXME duplicates bowtem_timeseries)
    locator = mpl.dates.MonthLocator([1, 4, 7, 10])
    formatter = mpl.dates.ConciseDateFormatter(
        locator, formats=['%b\n%Y', '%b']+['']*4, show_offset=False)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_minor_locator(mpl.dates.MonthLocator())
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=0, horizontalalignment='center')

    # plot directional components
    inset.plot(tilx, tily)
    tilx = tilx.resample('3ME').mean()
    tily = tily.resample('3ME').mean()
    inset.set_prop_cycle(None)
    inset.plot(tilx, tily, ls='none', marker='o', mfc='none')

    # set axes properties
    inset.set_xlabel('x-tilt')
    inset.set_ylabel('y-tilt')
    inset.yaxis.set_label_position('right')
    inset.yaxis.tick_right()

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
