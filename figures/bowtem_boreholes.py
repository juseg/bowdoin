#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature borehole setup."""

import absplots as apl
import matplotlib.pyplot as plt

import bowtem_utils


def subplots():
    """Initialize figure with map, profile axes and insets."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    fig.add_axes_mm([2.5, 2.5, 60, 85])
    fig.add_axes_mm([5, 5, 10, 15])
    fig.add_axes_mm([77.5, 12.5, 100, 75])

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=fig.axes[0], color='k')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[2], color='k')

    # return figure
    return fig


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
    fig = subplots()
    bowtem_utils.plot_bowdoin_map(fig.axes[0])
    bowtem_utils.plot_greenland_map(fig.axes[1])
    plot_long_profile(fig.axes[2])
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
