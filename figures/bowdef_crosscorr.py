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

# peak markers for the multi-day, daily and tidal bands
MARKERS = ['o', 's', '^']

# gnss record intervals for each year
YEARS = {
    '2015': ('20150516', '20150815'), '2016': ('20160610', '20160925'),
    '2017': ('20170526', '20170712')}


def correlate_bands(frame, var, ref, span, half):
    """Compute cross-correlations and pick delays within a search window."""

    # correlate with the UI06 tilt unit if the reference is also tilt
    ccorr = bowdef_utils.correlate_dataframes(
        frame[var], frame[ref]['UI06'] if ref == var else frame[ref],
        smin=f'-{span}', smax=span)

    # pick phase delays at the maximum correlation within the search window
    window = ccorr[abs(ccorr.index) <= pd.to_timedelta(half)]
    delay = -window.dropna(axis=1, how='all').idxmax()
    return ccorr, delay


def correlate_months(bands, var, ref, columns):
    """Pick delays over calendar months of every gnss record."""

    # for each band, collect delays of each month with enough data
    monthly = {}
    for band, frame, _, half in bands:
        frame = frame.reindex(columns=columns)
        delays = {}
        for start, end in YEARS.values():
            for month in pd.period_range(start, end, freq='M'):

                # clip the month to the gnss record, skip if shorter than 15 d
                start_time = max(month.start_time, pd.Timestamp(start))
                end_time = min(month.end_time, pd.Timestamp(end) +
                               pd.to_timedelta('1D') - pd.to_timedelta('1ns'))
                if end_time - start_time < pd.to_timedelta('15D'):
                    continue
                subset = frame.loc[start_time:end_time]

                # pick delays with lags limited to the search window
                _, delay = correlate_bands(subset, var, ref, half, half)

                # mask units with less than half of the month of valid pairs
                other = subset[ref]['UI06'] if ref == var else subset[ref]
                for unit in subset[var]:
                    pairs = subset[var, unit].notna() & other.get(
                        unit, other.squeeze()).notna()
                    if pairs.mean() < 0.5:
                        delay = delay.drop(unit, errors='ignore')
                delays[month] = delay

        # convert to a dataframe with months as rows
        monthly[band] = pd.DataFrame(delays).T
    return monthly


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


def plot_correlations(ax, ccorrs, delays, halves):
    """Plot cross-correlations and phase delays on one row per band."""

    # initialize regular subplots within the parent axes
    subaxes = ax.get_subplotspec().subgridspec(
        nrows=len(ccorrs), ncols=1, hspace=0.45).subplots()
    ax.set_axis_off()

    # for each band
    for ax, marker, (band, ccorr) in zip(subaxes, MARKERS, ccorrs.items()):
        delay = delays[band]

        # plot time delays in days beyond two days, else in hours
        span = ccorr.index.max()
        days = span > pd.to_timedelta('2D')
        unit = pd.to_timedelta('1D' if days else '1h')
        span = span / unit
        half = pd.to_timedelta(halves[band]) / unit

        # shade time delays outside the search window
        ax.axvspan(-span, -half, color='0.9', zorder=0)
        ax.axvspan(half, span, color='0.9', zorder=0)

        # plot cross-correlation (series.plot with deltas affected by #18910),
        # with hollow peak markers for the lower borehole (BH3) units
        ax.plot(-ccorr.index/unit, ccorr)
        for i, column in enumerate(ccorr):
            ax.plot(
                delay[column]/unit, ccorr[column][-delay[column]],
                color=f'C{i}', marker=marker,
                mfc='none' if column[0] == 'L' else None)

        # add band label, with the time delay unit
        ax.axvline(0.0, ls=':')
        ax.text(
            1.06, 0.5, f'{band.split()[0]} ({"d" if days else "h"})',
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

        # set axes properties
        ax.set_xlim(-span, span)
        ax.set_xticks(range(-10, 11, 5) if days else range(-36, 37, 12))
        ax.set_ylim(-1.2, 1.2)
        ax.set_yticks([-1, 0, 1])
        if not days:
            ax.xaxis.set_major_formatter(lambda x, pos: f'{x:g}'*(pos % 2))

    # set labels
    subaxes[-1].set_xlabel('time delay')
    subaxes[len(subaxes)//2].set_ylabel('cross-correlation', labelpad=2)

    # return subplots
    return subaxes


def plot_phase_delays(ax, depth, delays, monthly):
    """Plot phase delays against depth, one marker per band."""

    # plot phase delays, slightly offset in depth for each band, with hollow
    # markers for the lower borehole (BH3) units
    for k, (band, delay) in enumerate(delays.items()):
        delay = delay / pd.to_timedelta('1h')
        offset = 3*(k-1)
        for i, unit in enumerate(delay.index):
            ax.plot(
                delay[unit], depth.get(unit, 0)+offset, color=f'C{i}',
                marker=MARKERS[k], mfc='none' if unit[0] == 'L' else None)
        ax.plot([], [], color='0.25', ls='', marker=MARKERS[k],
                label=band.split()[0])

    # set axes properties, with symmetric limits of at least half a day and a
    # shaded one-hour band
    ax.axvline(0.0, ls=':')
    ax.axvspan(-1, 1, color='0.9', zorder=0)
    ax.invert_yaxis()
    ax.set_xlabel('phase delay (h)')
    ax.set_ylabel('sensor depth (m)')
    lim = max(12.5, 1.1 * max(abs(x) for x in ax.get_xlim()))
    ax.set_xlim(-lim, lim)

    # plot monthly delays at the same depths, clipped to the axes limits, as
    # ticks for melt-season (July and August) months and crosses otherwise
    for k, (band, delay) in enumerate(delays.items()):
        months = monthly[band].reindex(columns=delay.index)
        months = (months / pd.to_timedelta('1h')).clip(-lim, lim)
        melt = months.index.month.isin([7, 8])
        offset = 3*(k-1)
        for i, unit in enumerate(delay.index):
            for values, marker in [(months[unit][melt], '|'),
                                   (months[unit][~melt], 'x')]:
                ax.plot(values, [depth.get(unit, 0)+offset]*len(values),
                        color=f'C{i}', ls='', marker=marker, ms=4, mew=0.75,
                        zorder=1)
    ax.plot([], [], color='0.25', ls='', marker='|', label='July–Aug.')
    ax.plot([], [], color='0.25', ls='', marker='x', label='other months')

    # force axes limits on surface speed
    if 'GNSS' in delays['multi-day']:
        ax.set_ylim(103, -23)

    # extend upper limit to make room for a two-column legend
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom, top - 0.35*(bottom-top))
    ax.legend(loc='upper right', bbox_to_anchor=(1, 0.92), ncols=2,
              fontsize=6, columnspacing=1, handletextpad=0.5)


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
        ax.tick_params(labelleft=i == df[var].shape[1]-1)

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

    # set labels (centred on primary variable axes, upper of two middle ones)
    # and remove empty headlines in date tick labels
    subaxes[(df[var].shape[1]-1)//2].set_ylabel(ylabel.get(var))
    subaxes[-1].set_xlabel('')


def plot(couple='tilts_speed', year='2015'):
    """Plot and return full figure for given options."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    fig.subplots_mm(ncols=1, gridspec_kw={
        'left': 10, 'right': 127.5, 'bottom': 12.5, 'top': 2.5})
    fig.subplots_mm(ncols=2, gridspec_kw={
        'left': 72.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5,
        'wspace': 17.5})

    # load all variables
    depth = bowstr_utils.load(variable='dept').iloc[0]
    df = bowdef_utils.load_multivariate(filt='24hbp', join='inner')

    # extract multi-day (difference of 12-hour and 10-day kernel fits), daily
    # and tidal components of the correlated variables over the full record,
    # so that the time interval edges are not affected
    keys = dict(tilts='tilt', speed='gnss', stress='pres', tides='tide')
    var, ref = (keys[k] for k in couple.split('_'))
    subset = df.loc[:, df.columns.isin([var, ref], level='variable')]
    multiday = (
        bowdef_utils.filter_kernel_dataframe(subset, '12h') -
        bowdef_utils.filter_kernel_dataframe(subset, '10D'))
    daily = filter_harmonic_dataframe(subset, '24h')
    tidal = filter_harmonic_dataframe(subset, '12.42h')

    # select the gnss record of given year and drop empty records
    start, end = YEARS[year]
    df = df.loc[start:end]
    df = df.dropna(how='all', axis=1)

    # FIXME drop units missing from a multi-unit reference (UI05 tilt masked
    # by sensor saturation in 2017 stress_tilts), remove with stress cleanup
    if ref != var and df[ref].shape[1] > 1:
        df = df.drop(columns=df[var].columns.difference(df[ref].columns),
                     level='unit')

    # compute cross-correlations for each band over a range of time delays,
    # and pick phase delays at the maximum correlation within a search window
    # (half a period for the daily and tidal components)
    bands = [
        ('multi-day', multiday, '10D', '5D'),
        ('daily (24 h)', daily, '36h', '12h'),
        ('tidal (12.42 h)', tidal, '36h', '6.21h')]
    ccorrs, delays, halves = {}, {}, {}
    for band, frame, span, half in bands:
        frame = frame.reindex(index=df.index, columns=df.columns)
        ccorr, delay = correlate_bands(frame, var, ref, span, half)
        ccorrs[band], delays[band], halves[band] = ccorr, delay, half

    # pick delays over calendar months of every gnss record, for the units
    # of the selected year
    monthly = correlate_months(bands, var, ref, df.columns)

    # plot time series, correlations and phase delays
    tsax, ccax, pdax = fig.axes
    plot_time_series(tsax, depth, df, var, ref)
    ccaxes = plot_correlations(ccax, ccorrs, delays, halves)
    plot_phase_delays(pdax, depth, delays, monthly)

    # add subfigure labels
    for ax, label in zip([tsax, *ccaxes, pdax], 'abcde'):
        bowtem_utils.add_subfig_label(f'({label})', ax=ax)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    couples = [
        'speed_tides', 'stress_speed', 'stress_tides', 'stress_tilts',
        'tilts_speed', 'tilts_tides', 'tilts_tilts']
    years = ['2015', '2016', '2017']
    plotter = bowstr_utils.MultiPlotter(plot, couples=couples, years=years)
    plotter()


if __name__ == '__main__':
    main()
