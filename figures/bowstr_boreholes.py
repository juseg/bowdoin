#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides borehole setup."""

import xarray as xr
import absplots as apl
import hyoga
import bowtem_utils
import bowstr_utils

COLOURS = dict(bh1='C0', bh3='C6')


def init_figure():
    """Initialize figure with map and profile subplots."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    ax0 = fig.add_axes_mm([2.5, 2.5, 60, 85])
    ax1 = fig.add_axes_mm([77.5, 12.5, 100, 75])

    # add subfigure labels
    bowtem_utils.add_subfig_labels(fig.axes, colors=('w', 'k'))

    # return figure and axes
    return fig, (ax0, ax1)


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

    # add boreholes and camp waypoints for each borehole
    locations = bowtem_utils.read_locations_dict('../data/locations.gpx')
    for bh in ('bh1', 'bh3'):
        point = 'se' if bh == 'bh1' else 'nw'
        kwa = dict(ax=ax, color=COLOURS[bh], point=point)
        crs = '+proj=utm +zone=19'
        bowtem_utils.annotate_location(
            locations['B14'+bh.upper()], crs, text='2014', **kwa)
        bowtem_utils.annotate_location(
            locations['B16'+bh.upper()], crs, text='2016', **kwa)
        bowtem_utils.annotate_location(
            locations['B17'+bh.upper()], crs, text='2017', **kwa)
    bowtem_utils.annotate_location(
        locations['Tent Swiss'], crs, ax=ax, color='w', point='s',
        marker='^', text='Camp')

    # add scale
    img.to_dataset().hyoga.plot.scale_bar(ax=ax, color='w')

    # remove title
    ax.set_title("")


def plot_long_profile(ax):
    """Draw boreholes long profile with intrumental setup."""

    # draw vertical lines symbolising the boreholes
    for bh, color in COLOURS.items():
        base = bowtem_utils.load(
            '../data/processed/bowdoin.'+bh+'.inc.base.csv')
        base = base.iloc[0].squeeze()
        dist = dict(bh1=2, bh3=1.84)[bh]
        ax.plot([dist, dist], [base, 0.0], 'k-_')
        ax.text(dist, -5.0, bh.upper(), color=color, fontweight='bold',
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
    fig, (ax0, ax1) = init_figure()
    plot_location_map(ax0)
    plot_long_profile(ax1)
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
