#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature borehole setup."""

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import absplots as apl
import cartowik.annotations as can
import util.com
import cartowik.naturalearth as cne
import util.geo
import util.tem


def init_figure():
    """Initialize figure with map and profile subplots."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    ax0 = fig.add_axes_mm([2.5, 2.5, 60, 85], projection=ccrs.UTM(19))
    ax1 = fig.add_axes_mm([77.5, 12.5, 100, 75])

    # add subfigure labels
    util.com.add_subfig_label(ax=ax0, text='(a)', color='k')
    util.com.add_subfig_label(ax=ax1, text='(b)')

    # return figure and axes
    return fig, (ax0, ax1)


def plot_location_map(ax):
    """Draw boreholes location map with Sentinel image background."""

    # prepare map axes
    ax.set_extent([508e3, 512e3, 8621e3, 8626e3+2e3/3], crs=ax.projection)

    # plot Sentinel image data
    filename = '../data/external/20170310_174129_456_S2A_RGB.jpg'
    img = xr.open_dataarray(filename).astype(int)
    img = img.clip(0, None)  # replace no data with black
    img.plot.imshow(ax=ax, interpolation='bilinear')

    # add boreholes and camp waypoints for each borehole
    locations = util.geo.read_locations('../data/locations.gpx')
    for bh in ('bh1', 'bh2', 'bh3'):
        point = 'se' if bh == 'bh1' else 'nw'
        kwa = dict(ax=ax, color=util.tem.COLOURS[bh], point=point)
        can.annotate_location(locations['B14'+bh.upper()], text='2014', **kwa)
        can.annotate_location(locations['B16'+bh.upper()], text='2016', **kwa)
        can.annotate_location(locations['B17'+bh.upper()], text='2017', **kwa)
    can.annotate_location(locations['Tent Swiss'], ax=ax, color='k', point='s',
                          marker='^', text='Camp')

    # add scale
    util.com.add_scale_bar(ax=ax, color='k', label='1km', length=1000)

    # add invisible axes
    # FIXME add minimap util, and maybe cartowik example
    ax = ax.figure.add_axes_mm([5, 5, 10, 15], projection=ccrs.Stereographic(
        central_latitude=90, central_longitude=-45, true_scale_latitude=70))
    ax.set_extent([-1000e3, 1000e3, -3500e3, -500e3], crs=ax.projection)
    ax.patch.set_visible(False)
    ax.spines['geo'].set_visible(False)

    # draw minimap
    can.annotate_location(locations['B16BH1'], ax=ax, color='k')
    cne.add_countries(ax=ax, facecolor='none', scale='110m',
                      subject='Greenland', subject_edgecolor='k',
                      subject_facecolor='none')

    # remove title
    ax.set_title("")


def plot_long_profile(ax):
    """Draw boreholes long profile with intrumental setup."""

    # borehole plot properties
    distances = dict(bh1=2.015, bh2=1.985, bh3=1.84, err=1.84)

    # for each borehole
    for bh, color in util.tem.COLOURS.items():

        # draw a vertical line symbolising the borehole
        _, dept, base = util.tem.load_all(bh)
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
    labels = ['Inclinometers', 'Thermistors', 'Piezometers']
    markers = [util.tem.MARKERS[l[0]] for l in labels]
    handles = [plt.Line2D([], [], ls='none', marker=m) for m in markers]
    ax.legend(handles, labels, bbox_to_anchor=(1.0, 0.90), loc='upper right')

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
