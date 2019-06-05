#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature borehole setup."""

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartowik.annotations as can
import absplots as apl
import util


def init_figure():
    """Initialize figure with map and profile subplots."""

    # initialize figure
    # FIXME implement add_axes_mm / add_subplot_mm for unique subplots
    fig = apl.figure_mm(figsize=(150, 75))
    gridspec_kw = dict(left=2.5, right=87.5, bottom=2.5, top=2.5)
    ax0 = fig.subplots_mm(gridspec_kw=gridspec_kw,
                          subplot_kw=dict(projection=ccrs.UTM(19)))
    gridspec_kw = dict(left=75, right=2.5, bottom=10, top=2.5)
    ax1 = fig.subplots_mm(gridspec_kw=gridspec_kw)

    # add subfigure labels
    util.com.add_subfig_label(ax=ax0, text='(a)', color='w')
    util.com.add_subfig_label(ax=ax1, text='(b)')

    # return figure and axes
    return fig, (ax0, ax1)


def plot_location_map(ax):
    """Draw boreholes location map with Sentinel image background."""

    # prepare map axes
    ax.set_rasterization_zorder(2.5)
    ax.set_extent([507.6e3, 512.4e3, 8620.7e3, 8626.3e3], crs=ax.projection)

    # plot Sentinel image data
    filename = '../data/external/S2A_20160808_175915_456_RGB.jpg'
    xr.open_rasterio(filename).plot.imshow(ax=ax)

    # add boreholes and camp waypoints for each borehole
    locations = util.geo.read_locations('../data/locations.gpx')
    for bh in ('bh1', 'bh2', 'bh3'):
        point = 'se' if bh == 'bh1' else 'nw'
        kwa = dict(ax=ax, color=util.tem.COLOURS[bh], point=point)
        can.annotate_location(locations['B14'+bh.upper()], text='2014', **kwa)
        can.annotate_location(locations['B16'+bh.upper()], text='2016', **kwa)
        can.annotate_location(locations['B17'+bh.upper()], text='2017', **kwa)
    can.annotate_location(locations['Tent Swiss'], ax=ax, color='w', point='s',
                          marker='^', text='Camp')

    # add scale
    util.geo.add_scale_bar(ax=ax, length=1000, label='1km', color='w')


def plot_long_profile(ax):
    """Draw boreholes long profile with intrumental setup."""

    # borehole plot properties
    distances = dict(bh1=2.015, bh2=1.985, bh3=1.85, err=1.85)

    # for each borehole
    for bh, color in util.tem.COLOURS.items():

        # draw a vertical line symbolising the borehole
        temp, dept, base = util.tem.load_all(bh)
        dist = distances[bh]
        if bh != 'err':
            ax.plot([dist, dist], [base, 0.0], 'k-_')
            ax.text(dist, -5.0, bh.upper(), color=color, fontweight='bold',
                    ha='center', va='bottom')
            ax.text(dist, base+5.0, '{:.0f} m'.format(base),
                    ha='center', va='top')

        # locate the different units along that line
        for unit, dept in dept.items():
            sensor = unit[1]
            marker = util.tem.MARKERS[sensor]
            offset = 0.01 if sensor == 'I' else -0.01
            ax.plot(dist+1*offset, dept, color=color, marker=marker,
                    label='', ls='')
            ax.text(dist+2*offset, dept, unit, color=color,
                    ha=('left' if offset > 0 else 'right'),
                    va=('bottom' if unit in ('LP') else
                        'top' if unit in ('LT01', 'UT01') else
                        'center'))

    # add flow direction arrow
    ax.text(0.9, 0.55, 'ice flow', ha='center', transform=ax.transAxes)
    ax.annotate('', xy=(0.85, 0.5), xytext=(0.95, 0.5),
                xycoords=ax.transAxes, textcoords=ax.transAxes,
                arrowprops=dict(arrowstyle='->', lw=1.0))

    # add standalone legend
    labels = ['Inclinometers', 'Thermistors', 'Piezometres']
    markers = [util.tem.MARKERS[l[0]] for l in labels]
    handles = [plt.Line2D([], [], ls='none', marker=m) for m in markers]
    ax.legend(handles, labels, bbox_to_anchor=(1.0, 0.90))

    # set axes properties
    ax.set_xlim(1.75, 2.15)
    ax.set_ylim(292, -20)
    ax.set_xticks([1.85, 2.0])
    ax.set_xlabel('approximate distance from front in 2014 (km)')
    ax.set_ylabel('depth (m)')


def main():
    """Main program called during execution."""
    fig, (ax0, ax1) = init_figure()
    plot_location_map(ax0)
    plot_long_profile(ax1)
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
