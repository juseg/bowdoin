#!/usr/bin/env python
# Copyright (c) 2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation M2 tidal tilt amplitude and lag."""

import absplots as apl
import numpy as np
import pandas as pd

import bowstr_utils


def fit_tides_dataframe(df, *args, **kwargs):
    """Fit tidal harmonics on each series in a dataframe."""
    return pd.concat(
        {column: fit_tides_series(df[column], *args, **kwargs)
         for column in df}, axis=1, names=['series', 'tide', 'variable'])


def fit_tides_series(
        series, window='15D', stride='5D', start='2014-07-01',
        periods=None, polyorder=3, coverage=0.5, clip=5.0):
    """Fit tidal harmonics on a series in sliding windows.

    In each window, fit a polynomial trend plus a cosine and a sine at each
    tidal period by least squares on valid values, iteratively removing
    outliers beyond clip times the residual median absolute deviation.
    Return amplitude, phase (in degrees, relative to 2014-01-01 00:00 UTC
    so that windows and series can be compared) and their standard errors,
    as a dataframe with (tide, variable) columns indexed by window centre.
    Standard errors assume white residuals and may be underestimated.
    """

    # default to the main semidiurnal and diurnal tidal periods in hours
    if periods is None:
        periods = {'M2': 12.4206, 'S2': 12.0, 'K1': 23.9345, 'O1': 25.8193}
    omegas = 2 * np.pi / np.array(list(periods.values()))

    # prepare window starts and minimum number of valid values per window
    window = pd.to_timedelta(window)
    freq = pd.to_timedelta(pd.infer_freq(series.index))
    starts = pd.date_range(start, series.index[-1]-window, freq=stride)
    minimum = coverage * window / freq

    # loop on windows
    rows = {}
    for start in starts:
        chunk = series[start:start+window-freq].dropna()
        if len(chunk) < minimum:
            continue

        # build design matrix with trend (on normalized time) and harmonics
        hours = (chunk.index-pd.Timestamp('2014-01-01')).total_seconds()/3600
        hours = hours.to_numpy()
        normed = 2 * (chunk.index-start) / window - 1
        design = np.column_stack(
            [normed**k for k in range(polyorder+1)] +
            [f(omega*hours) for omega in omegas for f in (np.cos, np.sin)])

        # least-squares fit with iterative outlier removal
        values = chunk.to_numpy()
        keep = np.ones(len(values), dtype=bool)
        for _ in range(3):
            coefs = np.linalg.lstsq(design[keep], values[keep], rcond=None)[0]
            resid = values - design @ coefs
            keep = np.abs(resid) < clip * 1.4826 * np.median(
                np.abs(resid[keep]))

        # standard errors from the residual variance
        dof = keep.sum() - design.shape[1]
        cov = np.linalg.inv(design[keep].T @ design[keep])
        errs = (resid[keep]**2).sum() / dof * np.diag(cov)
        cosines, sines = coefs[polyorder+1::2], coefs[polyorder+2::2]
        errs = (errs[polyorder+1::2] + errs[polyorder+2::2]) / 2

        # amplitude and phase of a*cos(wt) + b*sin(wt) = A*cos(wt-phase)
        amplitude = np.hypot(cosines, sines)
        rows[start+window/2] = {
            (tide, variable): value for tide, *values in zip(
                periods, amplitude, np.degrees(np.arctan2(sines, cosines)),
                errs**0.5, np.degrees(errs**0.5/amplitude))
            for variable, value in zip(
                ['amplitude', 'phase', 'amplitude_se', 'phase_se'], values)}

    # return dataframe of fitted harmonics
    return pd.DataFrame.from_dict(rows, orient='index').rename_axis(
        series.index.name).rename_axis(['tide', 'variable'], axis=1)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 90), nrows=2, sharex=True, gridspec_kw={
            'left': 15, 'right': 2.5, 'bottom': 10, 'top': 2.5, 'hspace': 2.5})

    # load tilt angles and tides on a common 30-min grid
    tilx = bowstr_utils.load(variable='tilx').resample('30min').mean()
    tily = bowstr_utils.load(variable='tily').resample('30min').mean()
    tilt = np.degrees(np.arccos(np.cos(tilx)*np.cos(tily)))
    tide = bowstr_utils.load_pituffik_tides().resample('30min').mean()

    # fit tidal harmonics in sliding windows
    tilt = fit_tides_dataframe(tilt)
    tide = fit_tides_series(tide)

    # keep significant M2 amplitudes only (over three standard errors)
    tilt = tilt.xs('M2', axis=1, level='tide')
    amplitude = tilt.xs('amplitude', axis=1, level='variable')
    phase = tilt.xs('phase', axis=1, level='variable')
    phase = phase.where(amplitude > 3*tilt.xs(
        'amplitude_se', axis=1, level='variable'))
    amplitude = amplitude.where(phase.notna())
    tide = tide['M2']

    # plot M2 tilt rate amplitude (angle amplitude times angular frequency)
    rate = amplitude * 2 * np.pi / 12.4206 * 24 * 365
    rate.plot(
        ax=axes[0], marker='.', xlabel='',
        ylabel='M2 tilt rate\n' r'amplitude ($°\,a^{-1}$)')

    # plot M2 tilt delay after the Pituffik tide in hours (negative if ahead)
    lag = phase.sub(tide.phase.reindex(phase.index), axis=0)
    lag = (lag + 180) % 360 - 180
    lag = lag * 12.4206 / 360
    lag.plot(
        ax=axes[1], marker='.', legend=False, xlabel='',
        ylabel='M2 tilt delay\nafter tide (h)')

    # set axes properties
    axes[0].legend(loc='upper right', ncols=3)
    axes[0].set_xlim('20140701', '20170801')
    axes[0].set_ylim(0, 1)  # clips a few windows during borehole settling
    axes[1].set_ylim(-6.2, 6.2)
    axes[1].set_yticks([-6, -3, 0, 3, 6])

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
