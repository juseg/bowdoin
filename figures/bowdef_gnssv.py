#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation against GNSS velocity."""

import absplots as apl
import numpy as np
import pandas as pd

import bowdef_utils
import bowstr_utils
import bowtem_utils


def read_gnss_velocities(borehole=1):
    """Compute velocity components from raw data of one station."""
    # FIXME alternate velocity computations may be moved to postprocessing, and
    # the Zenodo dataset updated with central, multipoint or filtered velocity
    # (instead of two-point backward) and corrected azimuth formula. Or we
    # move all velocity derivations here and remove them from Zenodo.

    # read gps data, including backward velocity
    # FIXME implement reading data from other stations
    assert borehole == 1
    df = bowtem_utils.load('../data/processed/bowdoin.bh1.gps.csv')

    # compute two-point central velocity
    pos = df[['x', 'y', 'z']]
    vel = (pos.shift(1)-pos.shift(-1))/2
    df['vh1'] = (vel['x']**2 + vel['y']**2)**0.5 * 60 * 24 * 365 / 15.0

    # compute four-point central velocity
    vel = (pos.shift(-2)-8*pos.shift(-1)+8*pos.shift(1)-pos.shift(2))/12
    df['vh2'] = (vel['x']**2 + vel['y']**2)**0.5 * 60 * 24 * 365 / 15.0

    # compute Savitzky–Golay filtered velocity (6h = 24*15min)
    vel = bowdef_utils.filter_savgol_dataframe(
        df[['x', 'y']], window_length=48, polyorder=2, delta=1, deriv=1)
    df['vhs'] = (vel['x']**2 + vel['y']**2)**0.5 * 60 * 24 * 365 / 15.0

    # return the whole dataframe
    return df


def read_gnss_strain(lower=1, upper=3):
    """Compute longitudinal strain from raw data of two stations."""
    # FIXME reading GNSS data from other stations is not yet implemented

    ldf = read_gnss_velocities(borehole=lower)
    udf = read_gnss_velocities(borehole=upper)
    distance = ((ldf.x - udf.x) ** 2 + (ldf.y - udf.y) ** 2) ** 0.5
    strain = (distance.diff(1) - distance.diff(-1)) / 2.0
    return strain


def read_gnss_strain_rate(lower=1, upper=2):
    """Compute longitudinal strain rate from raw data of two stations."""
    # FIXME reading GNSS data from other stations is not yet implemented

    ldf = read_gnss_velocities(borehole=lower)
    udf = read_gnss_velocities(borehole=upper)
    distance = ((ldf.x - udf.x) ** 2 + (ldf.y - udf.y) ** 2) ** 0.5
    strain_rate = (ldf.fvh - udf.fvh) / distance
    return strain_rate


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=4, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 12.5, 'bottom': 12.5, 'top': 2.5,
            'height_ratios': (3, 3, 2, 1), 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # plot borehole velocity
    df = read_gnss_velocities()
    df.vh1.plot(ax=axes[0], color='0.9')
    df.vhs.plot(ax=axes[0], color='tab:blue')

    # read strain rate
    # strain = read_gnss_strain_rate()
    # strain.plot(ax=axes[1])

    # highpass-filter stress series
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(filt=None, resample='10min', tide=True)
    tide = pres.pop('tide')
    pres = pres / 1e3

    # plot tilt rate (6h = 36*10min)
    tilx = bowstr_utils.load(variable='tilx').resample('10min').mean()
    tily = bowstr_utils.load(variable='tily').resample('10min').mean()
    tilx = tilx.interpolate(limit_area='inside', method='linear')
    tily = tily.interpolate(limit_area='inside', method='linear')
    kwargs = {'window_length': 72, 'polyorder': 2, 'delta': 1, 'deriv': 1}
    tilx = bowdef_utils.filter_savgol_dataframe(tilx, **kwargs)
    tily = bowdef_utils.filter_savgol_dataframe(tily, **kwargs)
    tilt = np.arccos(np.cos(tilx)*np.cos(tily)) * 180 / np.pi
    tilt = tilt[tilt.index >= '2014-07-17']
    tilt *= 3600 * 24 * 365.25 / pd.to_timedelta('10min').total_seconds()
    tilt.plot(ax=axes[1], legend=False)

    # plot stress and tide data
    pres.plot(ax=axes[2], legend=False)
    tide.plot(ax=axes[3], c='C9')

    # add labels
    for i, unit in enumerate(pres):
        axes[2].text(
            1.01, 1.6-0.2*i, f'{unit}\n{depth[unit]:.0f}' r'$\,$m',
            color=f'C{i}', fontsize=6, fontweight='bold',
            transform=axes[2].transAxes)
    axes[3].text(
        1.01, 0, 'Pituffik\ntide'+r'$\,/\,$10', color='C9',
        fontsize=6, fontweight='bold', transform=axes[3].transAxes)

    # set axes limits
    axes[0].grid(which='minor')
    axes[1].grid(which='minor')
    axes[2].grid(which='minor')
    axes[3].set_xlabel('')
    axes[0].set_ylabel(r'velocity ($m\,a^{-1}$)', labelpad=0)
    axes[1].set_ylabel(r'tilt rate ($°\,a^{-1}$)')
    axes[2].set_ylabel('stress (MPa)')
    axes[3].set_ylabel('tide (kPa)', labelpad=0)
    axes[0].set_ylim(-50, 950)
    axes[1].set_ylim(-1, 21)
    axes[2].set_ylim(-0.15, 3.15)
    axes[3].set_ylim(-2.4, 2.4)

    # zoom on tidal oscillations
    # axes[0].set_xlim('20160801', '20161001')
    # axes[1].set_ylim(-1, 14)
    # axes[2].set_ylim(1.99, 2.14)

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
