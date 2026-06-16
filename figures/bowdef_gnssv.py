#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation against GNSS velocity."""

import absplots as apl
import numpy as np
import pandas as pd
import pyproj
import scipy

import bowstr_utils
import bowtem_utils


def read_gnss_velocities(borehole=1):
    """Compute velocity components from raw data of one station."""
    # FIXME alternate velocity computations may be moved to postprocessing, and
    # the Zenodo dataset updated with central, multipoint or filtered velocity
    # (instead of two-point backward) and corrected azimuth formula. Or we
    # move all velocity derivations here and remove them from Zenodo.

    # read gps data, including backward velocity
    df = bowtem_utils.load('../data/processed/bowdoin.bh1.gps.csv')

    # compute two-point central velocity
    pos = df[['x', 'y', 'z']]
    vel = (pos.shift(1)-pos.shift(-1))/2
    df['vh1'] = (vel['x']**2 + vel['y']**2)**0.5 * 60 * 24 * 365 / 15.0

    # compute four-point central velocity
    vel = (pos.shift(-2)-8*pos.shift(-1)+8*pos.shift(1)-pos.shift(2))/12
    df['vh2'] = (vel['x']**2 + vel['y']**2)**0.5 * 60 * 24 * 365 / 15.0

    # compute Savitzky–Golay filtered velocity (6h = 24*15min)
    vel = {dim: scipy.signal.savgol_filter(
        df[dim], window_length=48, polyorder=2, delta=1, deriv=1)
        for dim in ['x', 'y']}
    df['vhs'] = (vel['x']**2 + vel['y']**2)**0.5 * 60 * 24 * 365 / 15.0

    # return the whole dataframe
    return df


def read_gnss_strain(lower=1, upper=3):
    """Compute longitudinal strain from raw data of two stations."""

    ldf = read_gnss_velocities(borehole=lower)
    udf = read_gnss_velocities(borehole=upper)
    distance = ((ldf.x - udf.x) ** 2 + (ldf.y - udf.y) ** 2) ** 0.5
    strain = (distance.diff(1) - distance.diff(-1)) / 2.0
    return strain


def read_gnss_strain_rate(lower=1, upper=2):
    """Compute longitudinal strain rate from raw data of two stations."""

    ldf = read_gnss_velocities(borehole=lower)
    udf = read_gnss_velocities(borehole=upper)
    distance = ((ldf.x - udf.x) ** 2 + (ldf.y - udf.y) ** 2) ** 0.5
    strain_rate = (ldf.fvh - udf.fvh) / distance
    return strain_rate


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=3, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 12.5, 'bottom': 12.5, 'top': 2.5,
            'hspace': 12.5, 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # plot borehole velocity
    df = read_gnss_velocities(borehole=2)
    df.vh1.plot(ax=axes[0], alpha=0.25)
    df.vh2.plot(ax=axes[0], alpha=0.25)
    df.vhs.plot(ax=axes[0], alpha=1)

    # read strain rate
    # strain = read_gnss_strain_rate()
    # strain.plot(ax=axes[1])

    # highpass-filter stress series
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(filt=None, resample='10min', tide=True) / 1e3
    tide = pres.pop('tide')

    # plot tilt rate (6h = 36*10min)
    # FIXME add functions to savgol-derive series and dataframes?
    tilx = bowstr_utils.load(variable='tilx').resample('10min').mean()
    tily = bowstr_utils.load(variable='tily').resample('10min').mean()
    tilx = tilx.interpolate(limit_area='inside', method='cubic').dropna(how='all')
    tily = tily.interpolate(limit_area='inside', method='cubic').dropna(how='all')
    kwargs = dict(window_length=72, polyorder=2, delta=1, deriv=1)
    tilx = pd.concat([
        pd.Series(
            data=scipy.signal.savgol_filter(tilx[unit].dropna(), **kwargs),
            index=tilx[unit].dropna().index,
            name=unit) for unit in tilx], axis=1)
    tily = pd.concat([
        pd.Series(
            data=scipy.signal.savgol_filter(tily[unit].dropna(), **kwargs),
            index=tily[unit].dropna().index,
            name=unit) for unit in tily], axis=1)
    tilt = np.arccos(np.cos(tilx)*np.cos(tily)) * 180 / np.pi
    tilt = tilt[tilt.index >= '2014-07-17']
    tilt *= 3600 * 24 * 365.25 / pd.to_timedelta('10min').total_seconds()
    tilt.plot(ax=axes[1], xlabel='', ylabel=r'tilt rate ($°\,a^{-1}$)')

    # plot stress and tide data
    for ax in [axes[2]]:
        pres.plot(ax=ax, legend=False)
        tide.plot(ax=ax, c='C9')

        # set axes properties
        ax.grid(which='minor')
        ax.set_xlabel('')
        ax.set_ylabel('pressure or stress (MPa)')

        # add labels
        kwargs = {'fontsize': 6, 'fontweight': 'bold', 'transform': ax.transAxes}
        ax.text(1.01, 0, 'Pituffik\ntide' + r'$\,/\,$10', color='C9', **kwargs)
        for i, unit in enumerate(pres):
            ax.text(
                1.01, 0.9-0.1 * i, f"{unit}\n{depth[unit]:.0f}" r"$\,$m",
                color=f"C{i}", **kwargs)

    # set axes limits
    axes[1].legend(ncols=2)
    axes[0].grid(which='minor')
    axes[1].grid(which='minor')
    # axes[1].set_ylim(-2.5, 47.5)
    # axes[1].set_xlim('20150707', '20150721')
    # axes[1].set_xlim('20160613', '20160721')
    # axes[1].set_xlim('20160707', '20160721')
    axes[0].set_ylim(0, 1000)
    axes[1].set_ylim(-1, 21)

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
