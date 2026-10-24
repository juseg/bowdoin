#!/usr/bin/env python
# Copyright (c) 2015-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation 2D tilt animation."""

import absplots as apl
import matplotlib.animation
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


def update(date, collections, lines, text, tilx, tily):
    """Update 3D lines with dated tilt values."""
    for coll, line in zip(collections, lines):
        unit = line.get_label()
        x = np.array([0, tilx.loc[date, unit]])
        y = np.array([0, tily.loc[date, unit]])
        z = line.get_data_3d()[2]
        xyz_vertical = np.stack([0*x, 0*y, z])
        xyz_tilted = np.stack([x, y, z])
        coll.set_verts([np.concatenate((xyz_vertical.T, xyz_tilted.T[::-1]))])
        line.set_data_3d(xyz_tilted)
        text.set_text(f'{date:%d %b %Y\n%H:%M}')


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(192, 108), ncols=2, subplot_kw={'projection': '3d'})

    # load unit depths and tilt rates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    tilx, tily = load_tilt_rates_rotated(
        start='20150601', end='20150930', method='savgol', window='12h')

    # add additional smoothing
    tilx = tilx.resample('1h').mean()
    tily = tily.resample('1h').mean()

    # plot dummy arrows
    for unit, color in zip(depth.index, matplotlib.color_sequences['tab10']):
        x = [0, 1]
        y = [0, 0]
        z = [depth[unit], depth[unit]-50]
        ax = axes[{'L': 0, 'U': 1}[unit[0]]]
        ax.fill_between(x, y, z, x, y, z, alpha=0.5, color=color)
        ax.plot(x, y, z, color=color, label=unit)

        # set axes properties
        ax.set_proj_type('ortho')
        ax.set(xlim3d=(-1, 21), xlabel='mean-parallel')
        ax.set(ylim3d=(-2.2, 2.2), ylabel='mean-orthogonal')
        ax.set(zlim3d=(275, 75), zlabel='vertical')
        ax.view_init(azim=60)
        ax.set_title({'L': 'BH1', 'U': 'BH3'}[unit[0]])

    # add common legend and date label
    fig.legend(bbox_to_anchor=[0, 0, 1, 0.90], loc='upper center', ncols=3)
    text = fig.text(0.5, 0.1, 'date', ha='center')

    # save a preview
    collections = axes[0].collections + axes[1].collections
    lines = axes[0].lines + axes[1].lines
    update(tilx.index[0], collections, lines, text, tilx, tily)
    fig.savefig(__file__[:-3])

    # save animation
    ani = matplotlib.animation.FuncAnimation(
        fig, update, fargs=(collections, lines, text, tilx, tily),
        frames=tilx.index)
    ani.save(__file__[:-3] + '.mp4', fps=24)


if __name__ == '__main__':
    main()
