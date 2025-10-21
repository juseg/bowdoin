#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides borehole setup."""

import absplots as apl
import hyoga
import xarray as xr

import bowstr_utils
import bowtem_utils

COLOURS = dict(bh1='C0', bh3='C6')


def subplots():
    """Initialize figure with map, profile axes and insets."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    fig.add_axes_mm([2.5, 2.5, 60, 85])
    fig.add_axes_mm([5, 5, 10, 15])
    fig.add_axes_mm([77.5, 12.5, 100, 75])
    fig.add_axes_mm([135, 15, 40, 60])

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=fig.axes[0], color='w')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[2], color='k')
    bowtem_utils.add_subfig_label('(c)', ax=fig.axes[3], color='k')

    # return figure
    return fig


def plot_location_map(ax):
    """Draw boreholes location map with Sentinel image background."""

    # prepare map axes
    ax.set_xlim(508e3, 512e3)
    ax.set_ylim(8621e3, 8626e3+2e3/3)

    # plot Sentinel image data
    filename = '../data/native/20160808_175915_456_S2A_RGB.jpg'
    img = xr.open_dataarray(filename).astype(int)
    img = img.clip(0, None)  # replace no data with black
    img.plot.imshow(ax=ax, interpolation='bilinear')

    # add camp and boreholes locations
    crs = '+proj=utm +zone=19'
    bowtem_utils.annotate_location(
        'Tent Swiss', ax=ax, color='w', crs=crs, point='s', marker='^',
        text='Camp')
    for bh in ('bh1', 'bh3'):
        for year in (14, 16, 17):
            bowtem_utils.annotate_location(
                f'B{year}{bh.upper()}', ax=ax, color=COLOURS[bh],
                crs=crs, text=f'20{year}', point='se' if bh == 'bh1' else 'nw')

    # add scale
    img.to_dataset().hyoga.plot.scale_bar(ax=ax, color='w')

    # set axes properties
    ax.set_title('')
    ax.set_xlabel('')
    ax.set_xticks([])
    ax.set_ylabel('')
    ax.set_yticks([])


def plot_long_profile(ax):
    """Draw boreholes long profile with intrumental setup."""

    # same thing with new util
    bases = bowstr_utils.load(variable='base').iloc[0]
    for var, base in bases.items():
        color = {'BH1B': 'tab:blue', 'BH3B': 'tab:pink'}[var]
        dist = {'BH1B': 2, 'BH3B': 1.84}[var]
        ax.plot([dist, dist], [base, 0.0], 'k-_')
        ax.text(dist, -5.0, var[:3], color=color, fontweight='bold',
                ha='center', va='bottom')
        ax.text(dist, base+5.0, '{:.0f} m'.format(base),
                ha='center', va='top')

    # plot tilt unit depths
    depth = bowstr_utils.load(variable='dept').iloc[0]  # FIXME depth util?
    for i, unit in enumerate(depth.index):
        color = 'C%d' % i
        dist = dict(U=2, L=1.84)[unit[0]]
        ax.plot(dist+0.01, depth[unit], marker='^')
        ax.text(dist+0.02, depth[unit], unit, color=color, va='center')

    # add flow direction arrow
    ax.text(0.9, 0.55, 'ice flow', ha='center', transform=ax.transAxes)
    ax.annotate('', xy=(0.85, 0.5), xytext=(0.95, 0.5),
                xycoords=ax.transAxes, textcoords=ax.transAxes,
                arrowprops=dict(arrowstyle='->', lw=1.0))

    # set axes properties
    ax.set_xlim(1.74, 2.16)
    ax.set_ylim(292, -20)
    ax.set_xticks([1.84, 2.0])
    ax.set_xlabel('approximate distance from front in 2014 (km)')
    ax.set_ylabel('initial depth (m)')
    ax.grid(False, axis='x')


def main():
    """Main program called during execution."""
    fig = subplots()
    plot_location_map(fig.axes[0])
    plot_long_profile(fig.axes[2])
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
