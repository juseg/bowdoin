#!/usr/bin/env python
# Copyright (c) 2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin shear velocity against surface speed."""

import absplots as apl
import matplotlib as mpl
import numpy as np
import pandas as pd

import bowdef_utils
import bowstr_utils
from bowdef_utils import BOREHOLES, COLORS


def plot_slip_ratio_lines(ax, ratios=(93, 95, 97)):
    """Plot dotted lines of constant slip ratio with rotated labels."""
    speed = np.array([200, 900])
    for ratio in ratios:
        fraction = 1 - ratio/100
        ax.plot(speed, fraction*speed, color='0.5', ls=':', lw=0.8)

        # label where the line enters the axes, rotated along the line
        x = max(262, 10.6/fraction)
        (x0, y0), (x1, y1) = ax.transData.transform(
            [[x, fraction*x], [1.1*x, 1.1*fraction*x]])
        ax.text(x, fraction*x, f'{ratio} %', color='0.5', fontsize=6,
                rotation=np.degrees(np.arctan2(y1-y0, x1-x0)),
                rotation_mode='anchor', va='center', zorder=5,
                bbox={'fc': 'w', 'ec': 'none', 'pad': 0.5})


def load_daily_series():
    """Load daily shear velocities after closure, with their errors, and the
    daily surface speed."""

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

    # return daily means
    return series.resample('1D').mean(), speed.resample('1D').mean()


def plot_borehole(ax, bh, df, i=0):
    """Plot daily shear velocity against surface speed in one borehole,
    with a power-law fit, median error and labels stacked by i."""
    ax.scatter(
        df.speed, df.shear, s=4, color=COLORS[bh], alpha=0.5, linewidths=0.5)

    # fit and plot a power law of surface speed
    slope, constant = np.polyfit(np.log(df.speed), np.log(df.shear), 1)
    speed = np.array([df.speed.min(), df.speed.max()])
    ax.plot(speed, np.exp(constant)*speed**slope, color=COLORS[bh])

    # mark the median shear and error, mostly systematic
    ax.errorbar(
        760 - 40*i, df.shear.median(), yerr=df.shear_error.median(),
        color=COLORS[bh], marker='o', markersize=2, capsize=1, linewidth=1)

    # add borehole and slope labels
    ax.text(0.95, 0.05 + 0.2*i, f'slope {slope:.2f}', color=COLORS[bh],
            ha='right', transform=ax.transAxes)
    ax.text(0.95, 0.13 + 0.2*i, bh, color=COLORS[bh], fontweight='bold',
            ha='right', transform=ax.transAxes)


def plot_satellite_pairs(ax, shear):
    """Plot shear velocity averaged over satellite image pair intervals
    against satellite surface speed, with a median speed error bar."""
    sat = pd.concat([bowdef_utils.load_landsat_velocities(),
                     bowdef_utils.load_sentinel_velocities()])
    tab20 = mpl.color_sequences['tab20']
    for bh, color in [('BH1', tab20[1]), ('BH3', tab20[13])]:
        sat_shear = sat.apply(
            lambda row, bh=bh: shear[bh][row.start:row.end].mean(), axis=1)
        ax.scatter(
            sat.speed, sat_shear, s=4, color=color, alpha=0.5,
            marker='+', linewidths=0.5)

    # mark the median speed error below the 97 % line
    ax.errorbar(
        sat.speed.median(), 11, xerr=sat.error.median(), color='0.75',
        marker='+', markersize=2, capsize=1, linewidth=1)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(85, 60), gridspec_kw={
        'left': 12.5, 'bottom': 10, 'right': 2.5, 'top': 2.5})

    # set log axes first, as slip ratio labels follow the display slope
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(240, 800)
    ax.set_ylim(10, 40)
    plot_slip_ratio_lines(ax)

    # plot daily shear velocity against surface speed, BH3 labels at the
    # bottom and BH1 above
    series, speed = load_daily_series()
    for i, (bh, _) in enumerate(BOREHOLES):
        plot_borehole(ax, bh, series.xs(bh, axis=1, level=1).assign(
            speed=speed).dropna(), i=i)
    plot_satellite_pairs(ax, series.shear)

    # add legend with grey markers
    ax.scatter([], [], s=4, color='0.5', linewidths=0, label='GNSS')
    ax.scatter([], [], s=4, color='0.5', marker='+', linewidths=1,
               label='satellite')
    ax.legend(loc='upper left', markerscale=2)

    # set axes properties
    ax.set_xlabel(r'surface speed ($m\,a^{-1}$)')
    ax.set_ylabel(r'shear velocity ($m\,a^{-1}$)', labelpad=0)
    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_major_formatter('{x:g}')
        axis.set_minor_formatter('{x:g}')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
