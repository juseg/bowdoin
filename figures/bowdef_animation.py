#!/usr/bin/env python
# Copyright (c) 2015-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation 2D tilt animation."""

import absplots as apl
import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np

import bowdef_utils
import bowstr_utils


def load_tilt_rates_rotated(start='2015', end='2017', **kwargs):
    """Load tilt rates along and across the mean tilt direction."""

    # load tilt rate components
    tilx = bowstr_utils.load(variable='tilx').resample('10min').mean()
    tily = bowstr_utils.load(variable='tily').resample('10min').mean()
    tilx = tilx.interpolate(limit_area='inside', method='linear')
    tily = tily.interpolate(limit_area='inside', method='linear')
    tilx = bowdef_utils.filter_derive_dataframe(tilx, **kwargs)
    tily = bowdef_utils.filter_derive_dataframe(tily, **kwargs)

    # select an interval
    tilx = tilx.loc[start:end]
    tily = tily.loc[start:end]

    # compute tilt and azimuth (exact counter-clockwise from the x axis)
    tilt = np.arccos(np.cos(tilx)*np.cos(tily))
    azim = np.atan2(np.tan(tily), np.tan(tilx))

    # compute mean azimuth (will not exactly align rotated data on the x axis,
    # but return in a zero mean azimuth, maybe good for a polar plot)
    # rotation = np.arctan2(np.sin(azim).mean(), np.cos(azim).mean())

    # compute azimuth of the mean tilt (will align rotated tilt on the x axis,
    # but return a non-zero mean azimuth, probably best for a cartesian plot)
    rotation = np.atan2(np.tan(tily.mean()), np.tan(tilx.mean()))

    # rotate the angles along main tilt direction
    tilx = np.arctan(np.tan(tilt)*np.cos(azim-rotation)) * 180 / np.pi
    tily = np.arctan(np.tan(tilt)*np.sin(azim-rotation)) * 180 / np.pi

    # return rotated tilt components
    return tilx, tily


def update(date, lines, tilx, tily):
    """Update 3D lines with dated tilt values."""
    for i, line in enumerate(lines):
        x = np.array([0, tilx.loc[date].iloc[i]])
        y = np.array([0, tily.loc[date].iloc[i]])
        z = line.get_data_3d()[2]
        array = np.stack([x, y, z])
        line.set_data_3d(array)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 90), ncols=2, subplot_kw={'projection': '3d'})

    # load unit depths and tilt rates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    tilx, tily = load_tilt_rates_rotated(
        start='20150527', end='20150608', method='savgol', window='12h')

    # plot dummy arrows
    for unit, color in zip(depth.index, matplotlib.color_sequences['tab10']):
        ax = axes[{'U': 0, 'L': 1}[unit[0]]]
        ax.plot([0, 0], [0, 0], [depth[unit], depth[unit]-10], color=color)

        # set axes properties
        ax.set(xlim3d=(-1, 11), xlabel='mean-parallel')
        ax.set(ylim3d=(-1, 1), ylabel='mean-orthogonal')
        ax.set(zlim3d=(250, 0), zlabel='vertical')

    # plot one frame
    lines = axes[0].lines + axes[1].lines
    update(tilx.index[0], lines, tilx, tily)

    # save
    fig.savefig(__file__[:-3])

    # assemble animation
    matplotlib.animation.FuncAnimation(
        fig, update, fargs=(lines, tilx, tily), frames=tilx.index,
        interval=5)
    plt.show()


if __name__ == '__main__':
    main()
