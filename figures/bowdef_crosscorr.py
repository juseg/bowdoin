#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation cross-correlation."""

import numpy as np
import pandas as pd
import absplots as apl
import bowdef_utils
import bowtem_utils
import bowstr_utils


def filter_harmonic_dataframe(df, period, *args, **kwargs):
    """Apply kernel-weighted harmonic fit on each series in a dataframe."""

    return pd.concat([filter_harmonic_series(
        df[column], period, *args, **kwargs) for column in df], axis=1)


def filter_harmonic_series(series, period, truncate=3.0, spread=0.8):
    """Extract a periodic component by Gaussian kernel-weighted harmonic fit.

    At each sample, fit a constant and a sinusoid of given period (a duration
    such as '24h') to valid values within the kernel support, weighted by a
    Gaussian of standard deviation one period, and return the fitted sinusoid
    at that sample. Missing values get zero weight. The fit coefficients are
    those of the weighted wavelet Z-transform (Foster, 1996) with a decay
    constant of 1/(8 pi^2). Results are masked where values are missing, and
    where the kernel-weighted time spread (standard deviation) of valid values
    falls below a fraction spread of the period, as in
    bowdef_utils.filter_kernel_series.
    """

    # infer sampling interval and convert period (kernel std) to samples
    freq = pd.to_timedelta(pd.infer_freq(series.index))
    sigma = pd.to_timedelta(period) / freq

    # prepare kernel on sample offsets, masked and centred values, and basis
    # functions (constant, cosine and sine) of absolute sample time
    radius = int(truncate*sigma + 0.5)
    offsets = np.arange(-radius, radius+1)
    kernel = np.exp(-0.5*(offsets/sigma)**2)
    valid = series.notna().to_numpy()
    values = np.where(valid, series-series.mean(), 0)
    phase = 2*np.pi*np.arange(len(series))/sigma
    basis = [np.ones(len(series)), np.cos(phase), np.sin(phase)]

    # weighted sums of offset powers (ws), of basis products (wb) and of
    # values times basis functions (vb) as convolutions (reversed offsets)
    def convolve(signal, power=0):
        return np.convolve(signal, kernel*(-offsets)**power, mode='same')
    ws = [convolve(valid, power) for power in range(3)]
    wb = np.array([[convolve(valid*bi*bj) for bj in basis] for bi in basis])
    vb = np.array([convolve(values*bi) for bi in basis])

    # solve weighted least squares for the local sinusoid where well spread
    with np.errstate(divide='ignore', invalid='ignore'):
        masked = ~(ws[2]/ws[0]-(ws[1]/ws[0])**2 >= (spread*sigma)**2)
    wb = wb.transpose(2, 0, 1)
    wb[masked] = np.eye(3)
    coefs = np.linalg.solve(wb, vb.T[..., None])[..., 0]
    filtered = coefs[:, 1]*basis[1] + coefs[:, 2]*basis[2]
    filtered[masked | ~valid] = np.nan

    # return new series with filtered values
    return pd.Series(filtered, index=series.index, name=series.name)


def plot_correlations(ax, ccorr, delay):
    """Plot cross-correlations and phase delays."""

    # plot cross-correlation (series.plot with deltas affected by #18910)
    ax.plot(-ccorr.index/pd.to_timedelta('1h'), ccorr)
    for i, unit in enumerate(ccorr):
        ax.plot(
            delay[unit]/pd.to_timedelta('1h'), ccorr[unit][-delay[unit]],
            color=f'C{i}', marker='o')

    # set axes properties
    ax.axvline(0.0, ls=':')
    ax.set_xticks(range(-36, 48, 12))
    ax.set_xlabel('time delay (h)')
    ax.set_ylabel('cross-correlation', labelpad=0)
    ax.xaxis.set_major_formatter(lambda x, pos: f'{x:g}'*(pos % 2))
    ax.yaxis.set_major_formatter(lambda y, pos: f'{y:g}'*(pos % 2))


def plot_phase_delays(ax, depth, delay):
    """Plot cross-correlations and phase delays."""

    # plot phase delays
    delay = delay / pd.to_timedelta('1h')
    for i, unit in enumerate(delay.index):
        ax.plot(delay[unit], depth.get(unit, 0), color=f'C{i}', marker='o')
        ax.text(delay[unit], depth.get(unit, 0)-1, f' {unit}', color=f'C{i}')

    # set axes properties
    ax.axvline(0.0, ls=':')
    ax.invert_yaxis()
    ax.set_xlabel('phase delay (h)')
    ax.set_ylabel('sensor depth (m)')
    ax.set_xlim(ax.get_xlim()[0], 1.2*ax.get_xlim()[1]-0.2*ax.get_xlim()[0])

    # force axes limits on surface speed
    if 'GNSS' in delay:
        ax.set_ylim(103, -23)


def plot_time_series(ax, depth, df, var, ref):
    """Plot relevant time series on just as many subsubplots."""

    # initialize subsubplots
    subaxes = bowstr_utils.subsubplots(
        ax.figure, [ax], nrows=df[var].shape[1]+(df[ref].shape[1]==1),
        sharey=False)[0]

    # hardcoded axes properties
    ylabel = {'pres': 'stress (kPa)', 'tilt': r'tilt rate ($°\,a^{-1}$)'}
    ylim = {
        'gnss': (200, 700), 'pres': (-20, 20), 'tide': (-20, 20),
        'tilt': (2, 13)}
    yticks = {
        'gnss': (300, 600), 'pres': (-10, 10), 'tide': (-10, 10),
        'tilt': (5, 10)}
    ytext = {
        'gnss': '\nSurface\nspeed\n'r'($m\,a^{-1}$)',
        'tide': 'Pituffik\ntide'r'$\,/\,$10'}

    # plot primary variable time series
    for i, unit in enumerate(df[var].columns):
        ax = subaxes[i]
        df[var, unit].plot(ax=ax, color=f'C{i}', legend=False)
        ax.text(
            1.08, 0.5,
            ytext.get(var, f'{unit}\n{depth.get(unit, 0):.0f}'r'$\,$m'),
            color=f'C{i}', fontsize=6, fontweight='bold', rotation='vertical',
            ha='center', va='center', transform=ax.transAxes)

        # set axes properties
        ax.get_lines()[0].set_clip_box(ax.figure.axes[0].bbox)
        ax.set_ylim(ylim.get(var, None))
        ax.set_yticks(yticks.get(var, ax.get_yticks()))
        ax.tick_params(labelleft=len(subaxes)-i in (1, 2))

    # plot reference variable time series
    if df[ref].shape[1] == 1:
        ax = subaxes[-1]
        df[ref].plot(ax=ax, color='tab:cyan', legend=False)
        ax.text(
            1.08, 0.5, ytext.get(ref), color='tab:cyan',
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

        # set axes properties
        ax.get_lines()[0].set_clip_box(ax.figure.axes[0].bbox)
        ax.set_ylim(ylim.get(ref, None))
        ax.set_yticks(yticks.get(ref, ax.get_yticks()))

    # set labels and remove empty headlines in date tick labels
    subaxes[df[var].shape[1]//2].set_ylabel(ylabel.get(var))
    subaxes[-1].set_xlabel('')


def plot(couple='tilts_speed', method='inner'):
    """Plot and return full figure for given options."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    fig.subplots_mm(ncols=1, gridspec_kw={
        'left': 10, 'right': 127.5, 'bottom': 12.5, 'top': 2.5})
    fig.subplots_mm(ncols=2, gridspec_kw={
        'left': 72.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5, 'wspace': 15})

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=fig.axes[0], loc='sw')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[1], loc='sw')
    bowtem_utils.add_subfig_label('(c)', ax=fig.axes[2], loc='sw')

    # load all variables
    depth = bowstr_utils.load(variable='dept').iloc[0]
    df = bowdef_utils.load_multivariate(filt='24hbp', join=method)

    # select time interval and drop empty records
    # df = df.loc['20140701':'20140831']  # 2014 with gnss but before refreezing
    # df = df.loc['20140916':'20141016']  # 2014 all units but no gnss data
    # df = df.loc['20150527':'20150608']  # 2015 spring tidal buildup
    # df = df.loc['20150704':'20150803']  # 2015 summer daily cycles
    # df = df.loc['20150723':'20150803']  # 2015 summer daily zoom
    # df = df.loc['20160601':'20160930']  # 2016 full gnss record
    # df = df.loc['20160701':'20160830']  # 2016 summer daily cycles
    # df = df.loc['20160901':'20160923']  # 2016 fall tidal cycles
    df = df.loc['20150516':'20150815']  # 2015 full gnss record
    df = df.dropna(how='all', axis=1)

    # compute cross-correlations and phase delays
    keys = dict(tilts='tilt', speed='gnss', stress='pres', tides='tide')
    var, ref = (keys[k] for k in couple.split('_'))
    ccorr = bowdef_utils.correlate_dataframes(
        df[var], df[ref]['LI05'] if ref == var else df[ref])
    delay = -abs(ccorr).idxmax()

    # to keep the delay between -6 and 6 hours use
    # delay = -ccorr[abs(ccorr.index) < pd.to_timedelta('6h')].idxmax()

    # plot time series, correlations and phase delays
    plot_time_series(fig.axes[0], depth, df, var, ref)
    plot_correlations(fig.axes[1], ccorr, delay)
    plot_phase_delays(fig.axes[2], depth, delay)

    # save partial
    # fig.axes[1].set_visible(False)
    # fig.axes[2].set_visible(False)
    # fig.savefig(f'{__file__[:-3]}_{filt}_01')
    # fig.axes[1].set_visible(True)
    # fig.savefig(f'{__file__[:-3]}_{filt}_02')
    # fig.axes[2].set_visible(True)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    couples = [
        'speed_tides', 'stress_speed', 'stress_tides', 'stress_tilts',
        'tilts_speed', 'tilts_tides', 'tilts_tilts']
    plotter = bowstr_utils.MultiPlotter(plot, couples=couples)
    plotter()


if __name__ == '__main__':
    main()
