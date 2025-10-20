#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature borehole setup."""

import absplots as apl
import hyoga
import matplotlib.pyplot as plt
import xarray as xr

import bowtem_utils


def init_figure():
    """Initialize figure with map and profile subplots."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    ax0 = fig.add_axes_mm([2.5, 2.5, 60, 85])
    ax1 = fig.add_axes_mm([77.5, 12.5, 100, 75])

    # add subfigure labels
    bowtem_utils.add_subfig_label(ax=ax0, text='(a)', color='k')
    bowtem_utils.add_subfig_label(ax=ax1, text='(b)')

    # return figure and axes
    return fig, (ax0, ax1)


def plot_location_map(ax):
    """Draw boreholes location map with Sentinel image background."""

    # prepare map axes
    ax.set_xlim(508e3, 512e3)
    ax.set_ylim(8621e3, 8626e3+2e3/3)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_xticks([])
    ax.set_yticks([])

    # plot Sentinel image data
    filename = '../data/native/20170310_174129_456_S2A_RGB.jpg'
    img = xr.open_dataarray(filename).astype(int)
    img = img.clip(0, None)  # replace no data with black
    img.plot.imshow(ax=ax, add_labels=False, interpolation='bilinear')

    # add camp and boreholes locations
    crs = '+proj=utm +zone=19'
    bowtem_utils.annotate_location(
        'Tent Swiss', ax=ax, color='k', crs=crs, point='s', marker='^',
        text='Camp')
    for bh in ('bh1', 'bh2', 'bh3'):
        for year in (14, 16, 17):
            bowtem_utils.annotate_location(
                f'B{year}{bh.upper()}', ax=ax, color=bowtem_utils.COLOURS[bh],
                crs=crs, text=f'20{year}', point='se' if bh == 'bh1' else 'nw')

    # add scale
    img.to_dataset().hyoga.plot.scale_bar(ax=ax)

    # add invisible axes
    ax = ax.figure.add_axes_mm([5, 5, 10, 15])
    ax.set_axis_off()
    ax.set_xlim(-1000e3, 1000e3)
    ax.set_ylim(-3500e3, -500e3)

    # draw minimap
    crs = '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45'
    countries = hyoga.open.natural_earth(
        'admin_0_countries', 'cultural', '110m')
    greenland = countries[countries.NAME == 'Greenland'].to_crs(crs)
    greenland.plot(ax=ax, facecolor='none', edgecolor='k')
    bowtem_utils.annotate_location('Tent Swiss', crs=crs, ax=ax, color='k')


def plot_long_profile(ax):
    """Draw boreholes long profile with intrumental setup."""

    # borehole plot properties
    distances = dict(bh1=2.015, bh2=1.985, bh3=1.84, err=1.84)

    # for each borehole
    for bh, color in bowtem_utils.COLOURS.items():

        # draw a vertical line symbolising the borehole
        _, dept, base = bowtem_utils.load_all(bh)
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
            marker = bowtem_utils.MARKERS[sensor]
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
    markers = [bowtem_utils.MARKERS[l[0]] for l in labels]
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
