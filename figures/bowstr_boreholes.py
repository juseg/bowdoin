#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides borehole setup."""

import xarray as xr
import cartopy.crs as ccrs
import absplots as apl
import cartowik.annotations as can
import util.com
import util.geo
import util.str

COLOURS = dict(bh1='C0', bh3='C6')


def init_figure():
    """Initialize figure with map and profile subplots."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    ax0 = fig.add_axes_mm([2.5, 2.5, 60, 85], projection=ccrs.UTM(19))
    ax1 = fig.add_axes_mm([77.5, 12.5, 100, 75])

    # add subfigure labels
    util.com.add_subfig_labels(fig.axes, colors=('w', 'k'))

    # return figure and axes
    return fig, (ax0, ax1)


def plot_location_map(ax):
    """Draw boreholes location map with Sentinel image background."""

    # prepare map axes
    ax.set_extent([508e3, 512e3, 8621e3, 8626e3+2e3/3], crs=ax.projection)

    # plot Sentinel image data
    filename = '../data/external/20160808_175915_456_S2A_RGB.jpg'
    img = xr.open_dataarray(filename).astype(int)
    img = img.clip(0, None)  # replace no data with black
    img.plot.imshow(ax=ax, interpolation='bilinear')

    # add boreholes and camp waypoints for each borehole
    locations = util.geo.read_locations('../data/locations.gpx')
    for bh in ('bh1', 'bh3'):
        point = 'se' if bh == 'bh1' else 'nw'
        kwa = dict(ax=ax, color=COLOURS[bh], point=point)
        can.annotate_location(locations['B14'+bh.upper()], text='2014', **kwa)
        can.annotate_location(locations['B16'+bh.upper()], text='2016', **kwa)
        can.annotate_location(locations['B17'+bh.upper()], text='2017', **kwa)
    can.annotate_location(locations['Tent Swiss'], ax=ax, color='w', point='s',
                          marker='^', text='Camp')

    # add scale
    util.com.add_scale_bar(ax=ax, color='w', label='1km', length=1000)

    # remove title
    ax.set_title("")


def plot_long_profile(ax):
    """Draw boreholes long profile with intrumental setup."""

    # draw vertical lines symbolising the boreholes
    for bh, color in COLOURS.items():
        base = util.com.load_file(
            '../data/processed/bowdoin.'+bh+'.inc.base.csv')
        base = base.iloc[0].squeeze()
        dist = dict(bh1=2, bh3=1.84)[bh]
        ax.plot([dist, dist], [base, 0.0], 'k-_')
        ax.text(dist, -5.0, bh.upper(), color=color, fontweight='bold',
                ha='center', va='bottom')
        ax.text(dist, base+5.0, '{:.0f} m'.format(base),
                ha='center', va='top')

    # plot tilt unit depths
    depth = util.str.load(variable='dept').iloc[0]  # FIXME depth util?
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
