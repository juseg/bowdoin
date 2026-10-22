#!/usr/bin/env python
# Copyright (c) 2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin shear velocity against surface speed."""

import absplots as apl
import matplotlib.lines
import numpy as np
import pandas as pd

import bowdef_utils
import bowstr_utils
from bowdef_utils import BOREHOLES, COLORS, LIGHT_COLORS


def plot_median_error(ax, median, error, position, axis='y', **kwargs):
    """Mark a median value by a dashed line across the axes, and its
    relative error by a bar at an axes fraction position along the line."""
    bounds = median*error
    kwargs = {'capsize': 1, 'linewidth': 1, **kwargs}
    line = {'color': kwargs['color'], 'ls': '--', 'lw': 0.5, 'zorder': 0}
    if axis == 'y':
        ax.axhline(median, **line)
        ax.errorbar(position, median, yerr=bounds,
                    transform=ax.get_yaxis_transform(), **kwargs)
    else:
        ax.axvline(median, **line)
        ax.errorbar(median, position, xerr=bounds,
                    transform=ax.get_xaxis_transform(), **kwargs)


def plot_slip_ratio_lines(ax, ratios=(93, 95, 97)):
    """Plot dotted lines of constant slip ratio across the axes, with rotated
    labels where they enter the axes."""
    speed = np.array(ax.get_xlim())
    for ratio in ratios:
        fraction = 1 - ratio/100
        ax.plot(speed, fraction*speed, color='0.5', ls=':', lw=0.8,
                scalex=False, scaley=False)

        # label just inside the left or bottom edge, rotated along the line
        x = 1.05 * max(speed[0], ax.get_ylim()[0]/fraction)
        (x0, y0), (x1, y1) = ax.transData.transform(
            [[x, fraction*x], [1.1*x, 1.1*fraction*x]])
        ax.text(x, fraction*x, f'{ratio} %', color='0.5', fontsize=6,
                rotation=np.degrees(np.arctan2(y1-y0, x1-x0)),
                rotation_mode='anchor', va='center', zorder=5,
                bbox={'fc': 'w', 'ec': 'none', 'pad': 0.5})


def load_series():
    """Load shear velocities after closure, with their errors, and the
    surface speed."""

    # load sensor depths, ice thickness, strain rates and surface speed
    base = bowstr_utils.load(variable='base').iloc[0]
    depth = bowstr_utils.load(variable='dept').iloc[0]
    strain = bowdef_utils.load_strain_rates(method='kernel', window='3h')
    speed = bowdef_utils.load_gnss_velocities(method='kernel', window='3h').vh

    # compute shear velocities as in slipratio and mask records before closure
    dates = bowdef_utils.load_freezing_dates()
    sigma = bowdef_utils.compute_residual_error(strain, depth, dates)
    series = bowdef_utils.compute_shear_series(strain, depth, base, sigma)
    for bh, _ in BOREHOLES:
        series.loc[series.index < dates[bh], (slice(None), bh)] = np.nan
    return series, speed


def plot_borehole(ax, bh, df, label_y, error_x):
    """Plot daily shear velocity against surface speed in one borehole,
    with a power-law fit, a median error bar and a label line, at axes
    fraction coordinates error_x and label_y."""
    ax.scatter(
        df.speed, df.shear, s=4, color=COLORS[bh], alpha=0.5, linewidths=0.5)

    # fit and plot a power law of surface speed
    slope, constant = np.polyfit(np.log(df.speed), np.log(df.shear), 1)
    speed = np.array([df.speed.min(), df.speed.max()])
    ax.plot(speed, np.exp(constant)*speed**slope, color=COLORS[bh])

    # mark the median shear and its median relative error, mostly systematic
    median = df.shear.median()
    plot_median_error(
        ax, median, df.shear_error.median() / median, error_x,
        color=COLORS[bh], marker='o', markersize=2)

    # add a label line, bold borehole name left of the slope
    ax.text(0.64, label_y, bh, color=COLORS[bh], fontweight='bold',
            transform=ax.transAxes)
    ax.text(0.74, label_y, f'(slope {slope:.2f})', color=COLORS[bh],
            transform=ax.transAxes)


def plot_satellite_pairs(ax, shear):
    """Plot shear velocity averaged over satellite image pair intervals
    against satellite surface speed, with a median speed error bar."""
    sat = pd.concat([bowdef_utils.load_landsat_velocities(),
                     bowdef_utils.load_sentinel_velocities()])
    sat_shear = bowdef_utils.compute_interval_means(shear, sat)
    for bh, color in LIGHT_COLORS.items():
        ax.scatter(
            sat.speed, sat_shear[bh], s=8, color=color, alpha=0.5,
            marker='+', linewidths=0.5, zorder=0)

    # mark the median speed and its median relative error above the 97 % label
    median = sat.speed.median()
    error = (sat.error / sat.speed).median()
    plot_median_error(
        ax, median, error, 0.12, axis='x', color='0.625', marker='+',
        markersize=3)

    # label the error bar above
    ax.annotate(
        'satellite', xy=(median, 0.12), xytext=(0, 3),
        xycoords=ax.get_xaxis_transform(), textcoords='offset points',
        color='0.625', fontsize=6, ha='center', va='bottom')


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(85, 60), gridspec_kw={
        'left': 12.5, 'bottom': 10, 'right': 2.5, 'top': 2.5})

    # set log axes first, as slip ratio labels follow the display slope
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(190, 780)
    ax.set_ylim(10, 40)
    plot_slip_ratio_lines(ax)

    # plot daily shear velocity against surface speed, BH3 label at the
    # bottom and BH1 above, BH1 error bar left of BH3, and satellite pairs
    # from full-resolution shear
    series, speed = load_series()
    daily = series.resample('1D').mean()
    daily_speed = speed.resample('1D').mean()
    for bh, label_y, error_x in [('BH3', 0.05, 0.975), ('BH1', 0.13, 0.955)]:
        plot_borehole(ax, bh, daily.xs(bh, axis=1, level=1).assign(
            speed=daily_speed).dropna(), label_y, error_x)
    plot_satellite_pairs(ax, series.shear)

    # add legend with grey markers twice the data size
    ax.legend(loc='upper left', handles=[
        matplotlib.lines.Line2D(
            [], [], ls='', marker='o', markersize=4, mew=1, color='0.25',
            alpha=0.5, label='GNSS'),
        matplotlib.lines.Line2D(
            [], [], ls='', marker='+', markersize=4, mew=1, color='0.625',
            label='satellite')])

    # set axes properties
    ax.set_xlabel(r'surface speed ($m\,a^{-1}$)')
    ax.set_ylabel(r'shear velocity ($m\,a^{-1}$)')
    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_major_formatter('{x:g}')
        axis.set_minor_formatter('{x:g}')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
