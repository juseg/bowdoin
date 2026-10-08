# Copyright (c) 2015-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Bowdoin deformation paper utils."""

import matplotlib as mpl
import numpy as np
import pandas as pd
import scipy as sp
import xarray as xr

import bowstr_utils
import bowtem_utils

# borehole names, unit prefixes, colours and seasonal windows
# FIXME: winter starts on Jan. 4 to skip the UI04 tilt offset jump of
# 2015 Jan. 2, restore Jan. 1 once the jump is fixed in preprocessing.
BOREHOLES = [('BH3', 'L'), ('BH1', 'U')]
COLORS = {'BH1': 'tab:blue', 'BH3': 'tab:pink'}
WINDOWS = [('2015-01-04', '2015-02-01', False),
           ('2015-07-01', '2015-08-01', True)]


# Signal processing methods
# -------------------------

def compute_power_fit(depth, strain):
    """Fit to a power law strain = constant * depth ** exponent."""
    log_strain = np.log(strain.dropna())
    log_depth = np.log(depth.reindex(log_strain.index))
    exponent, constant = np.polyfit(log_depth, log_strain, 1)
    return exponent, np.exp(constant)


def correlate_dataframes(frame, other, smin='-36h', smax='36h'):
    """Compute cross-correlations between columns of two dataframes."""

    # convert min and max shifts to integer
    freq = pd.to_timedelta(pd.infer_freq(frame.index))
    smin = int(pd.to_timedelta(smin)/freq)
    smax = int(pd.to_timedelta(smax)/freq)

    # compute correlations and phase delays
    return pd.concat([
        correlate_series(
            frame[col], other.get(col, other.squeeze()), smin, smax)
        for col in frame], axis=1)


def correlate_series(series, other, smin, smax):
    """Return cross-correlation between two series."""

    # prepare dataframe with shifted series
    shifts = np.arange(smin, smax+1)
    data = (series.shift(i, freq='infer') for i in shifts)
    index = shifts*pd.to_timedelta(pd.infer_freq(series.index))
    df = pd.DataFrame(data=data, index=index)

    # return correlation series (min_periods=10 removes warnings and artefacts)
    # NOTE in pandas >= 3 onwards one can pass min_periods to corrwith
    # df.corrwith(other, axis=1).rename(series.name)  # RuntimeWarning
    # df.corrwith(other, axis=1, min_periods=2).rename(series.name)  # pd >= 3
    return df.apply(
        lambda series: other.corr(series, min_periods=10), axis=1).rename(
            series.name)


def correlate_rolling_dataframes(frame, other, window='5D', stride='5D'):
    """Compute rolling-window cross-correlation between two dataframes."""

    # prepare rolling-window slicing
    index = frame.index
    window = pd.to_timedelta(window)
    starts = pd.date_range(start=index[0], end=index[-1]-window, freq=stride)
    slices = [slice(start, start+window) for start in starts]

    # compute rolling-window cross-correlation
    series = (
        correlate_dataframes(
            frame.loc[s], other.loc[s], '-12h', '12h').transpose().stack()
        for s in slices)
    mcorr = pd.DataFrame(data=series, index=starts+window/2)
    return mcorr


def filter_derive_dataframe(df, method='twopoint', window=None):
    """Derive a dataframe optionally using Savitsky-Golay filter."""

    # infer sampling interval in years
    delta = pd.to_timedelta(pd.infer_freq(df.index)) / pd.to_timedelta('365d')

    # compute two-point central difference
    if method == 'twopoint':
        return (df.shift(1)-df.shift(-1)) / 2 / delta

    # compute four-point central difference
    if method == 'fourpoint':
        return (
            df.shift(-2)-8*df.shift(-1)+8*df.shift(1)-df.shift(2)) / 12 / delta

    # compute Savitzky–Golay filtered derivative
    if method == 'savgol':
        return filter_savgol_dataframe(df, window, polyorder=2, deriv=1)

    # compute Gaussian kernel-weighted local linear derivative
    if method == 'kernel':
        return filter_kernel_dataframe(df, window, deriv=1)

    # other methods are unknown
    raise ValueError(f"Unknown derivation method {method}.")


def filter_kernel_dataframe(df, sigma, *args, **kwargs):
    """Apply kernel-weighted local linear fit on each series in a dataframe."""

    return pd.concat([filter_kernel_series(
        df[column], sigma, *args, **kwargs) for column in df], axis=1)


def filter_kernel_series(series, sigma, deriv=0, truncate=3.0, spread=0.8):
    """Apply Gaussian kernel-weighted local linear fit on a series.

    At each sample, fit a line to valid values within the kernel support,
    weighted by a Gaussian of standard deviation sigma (a duration such as
    '3h'), and return its value (deriv=0) or slope (deriv=1, per year).
    Missing values get zero weight, so no interpolation is needed across data
    gaps. Results are masked where the kernel-weighted time spread (standard
    deviation) of valid values falls below a fraction spread of sigma, its
    value for a full window. This masks run ends and short isolated runs, but
    not uniformly sparse sampling.
    """

    # infer sampling interval and convert standard deviation to samples
    freq = pd.to_timedelta(pd.infer_freq(series.index))
    sigma = pd.to_timedelta(sigma) / freq

    # prepare kernel on sample offsets, and masked and centred values
    # (centring avoids precision loss on large values such as UTM northings)
    radius = int(truncate*sigma + 0.5)
    offsets = np.arange(-radius, radius+1)
    kernel = np.exp(-0.5*(offsets/sigma)**2)
    valid = series.notna().to_numpy()
    values = np.where(valid, series-series.mean(), 0)

    # weighted sums of offset powers (ws) and values times offset powers (vs)
    # as convolutions (reversed offsets)
    def convolve(signal, power):
        return np.convolve(signal, kernel*(-offsets)**power, mode='same')
    ws = [convolve(valid, power) for power in range(3)]
    vs = [convolve(values, power) for power in range(2)]

    # solve weighted least squares for the local line where well spread
    with np.errstate(divide='ignore', invalid='ignore'):
        if deriv == 0:
            filtered = (ws[2]*vs[0]-ws[1]*vs[1]) / (ws[0]*ws[2]-ws[1]**2)
            filtered += series.mean()
        else:
            filtered = (ws[0]*vs[1]-ws[1]*vs[0]) / (ws[0]*ws[2]-ws[1]**2)
            filtered *= pd.Timedelta('365d') / freq
        filtered[~(ws[2]/ws[0]-(ws[1]/ws[0])**2 >= (spread*sigma)**2)] = np.nan

    # return new series with filtered values
    return pd.Series(filtered, index=series.index, name=series.name)


def filter_savgol_dataframe(df, window, *args, **kwargs):
    """Apply Savitsky-Golay filter on each series in a dataframe."""
    return pd.concat([filter_savgol_series(
        df[column], window, *args, **kwargs) for column in df], axis=1)


def filter_savgol_series(series, window, *args, **kwargs):
    """Apply Savitsky-Golay filter on each continuous stretch of a series.

    The window is a duration such as '12h', converted to an odd number of
    samples (rounding even counts up). Derivatives are per year.
    """

    # strip initial and final nan values
    first = series.first_valid_index()
    last = series.last_valid_index()
    series = series.loc[first:last]

    # infer sampling interval and convert window to odd number of samples
    freq = pd.to_timedelta(pd.infer_freq(series.index))
    delta = freq/pd.Timedelta('365d')
    window_length = int(pd.to_timedelta(window)/freq) // 2 * 2 + 1

    # label continuous stretches of valid values
    valid = series.notna()
    labels = (valid != valid.shift()).cumsum()[valid]

    # filter stretches at least as long as window, leave others as nan
    filtered = pd.Series(index=series.index, name=series.name, dtype=float)
    for _, stretch in series[valid].groupby(labels):
        if len(stretch) >= window_length:
            filtered[stretch.index] = sp.signal.savgol_filter(
                stretch, window_length, *args, delta=delta, **kwargs)

    # return new series with filtered values
    return filtered


# Data loading methods
# --------------------

def load_gnss_velocities(**kwargs):
    """Compute velocity components from raw data of one station."""
    # NOTE this improved velocity computation may be moved to postprocessing,
    # and the Zenodo dataset updated with centred-difference or filtered
    # (insead of backward) velocity and corrected azimuth formula. Or we
    # move all velocity derivations here and remove them from Zenodo.
    # NOTE we could add data from other stations (Sugiyama et al. 2024) and
    # methods to compute longitudinal strain and strain rates.
    # ldf = load_gnss_velocities(borehole=lower)
    # udf = load_gnss_velocities(borehole=upper)
    # distance = ((ldf.x - udf.x) ** 2 + (ldf.y - udf.y) ** 2) ** 0.5
    # strain = (distance.diff(1) - distance.diff(-1)) / 2.0
    # strain_rate = (ldf.fvh - udf.fvh) / distance

    # read reset-corrected gnss positions
    df = bowtem_utils.load('../data/processed/bowdoin.bh1.gps.csv')

    # derive horizontal velocity
    vel = filter_derive_dataframe(df[['x', 'y', 'z']], **kwargs)
    vel = vel.assign(vh=(vel.x**2 + vel.y**2)**0.5)

    # return velocity
    return vel


def load_landsat_velocities():
    """Load surface velocities from Landsat feature-tracking."""
    df = pd.read_csv(
        '../data/satellite/bowdoin-landsat.csv', parse_dates=['start', 'end'])
    df = df.assign(delay=df.end-df.start)
    df = df.set_index(df.start+df.delay/2)
    df = df.assign(delay=df.delay/pd.to_timedelta('1d'))
    df = df.rename(columns={'vel': 'speed', 'err': 'error'})
    return df


def load_sentinel_velocities():
    """Load surface velocities from Sentinel feature-tracking."""
    df = pd.read_csv(
        '../data/satellite/bowdoin-sentinel.txt', delimiter=',\\s+',
        engine='python', index_col='YYYY-MM-DD (avg)',
        parse_dates=['YYYY-MM-DD (1st)', 'YYYY-MM-DD (2nd)'])
    df = df.rename_axis(None).rename(columns={
        'time-diff (days)': 'delay', 'vel (m/a)': 'speed',
        'vel_error (m/a)': 'error', 'YYYY-MM-DD (1st)': 'start',
        'YYYY-MM-DD (2nd)': 'end'})
    return df


def load_strain_rates(**kwargs):
    """Load strain rates from filter-derived tilt component rates."""
    tilx, tily = load_tilt_component_rates(**kwargs)
    costilt = np.cos(tilx) * np.cos(tily)
    return 0.5 * (1 - costilt**2) ** 0.5 / costilt


def load_tilt_azimuth(**kwargs):
    """Load tilt direction from filter-derived tilt component rates."""
    tilx, tily = load_tilt_component_rates(**kwargs)
    azimuth = np.atan2(-np.sin(tilx)*np.cos(tily), np.sin(tily)) * 180 / np.pi
    azimuth = azimuth[azimuth.index >= '2014-07-17']
    return azimuth


def load_tilt_component_rates(method='twopoint', window=None):
    """Load resampled and filter-derived tilt rate components."""

    # load tilt components resampled on a regular 10-min grid
    tilx = bowstr_utils.load(variable='tilx').resample('10min').mean()
    tily = bowstr_utils.load(variable='tily').resample('10min').mean()

    # interpolate across gaps except for the gap-aware kernel fit
    if method != 'kernel':
        tilx = tilx.interpolate(limit_area='inside', method='linear')
        tily = tily.interpolate(limit_area='inside', method='linear')

    # return filter-derived tilt rate components
    return (filter_derive_dataframe(tilx, method=method, window=window),
            filter_derive_dataframe(tily, method=method, window=window))


def load_tilt_rates(**kwargs):
    """Load tilt rates from filter-derived tilt component rates."""
    tilx, tily = load_tilt_component_rates(**kwargs)
    tilt = np.arccos(np.cos(tilx)*np.cos(tily)) * 180 / np.pi
    tilt = tilt[tilt.index >= '2014-07-17']
    return tilt


def load_multivariate(join='inner', filt=None, method='kernel', window='3h'):
    """Load tilt rates, speed, stress, and tides in one dataframe."""

    # load all variables independently
    pres = bowstr_utils.load(filt=filt, resample='10min')
    azim = load_tilt_azimuth(method=method, window=window)
    tilt = load_tilt_rates(method=method, window=window)
    gnss = load_gnss_velocities(method=method, window=window).vh.rename('GNSS')
    tide = bowstr_utils.load_pituffik_tides().groupby(level=0).mean().rename(
        'TIDE')

    # prepare new index depending on join method
    # NOTE mixed method may fail on variable tilt sampling rate
    index = tilt.index.join(gnss.index, how=join.replace('mixed', 'left'))
    if join == 'outer':
        index = pd.date_range(index[0], index[-1], freq=index.diff().min())

    # reindex (tide is on a different grid, so upsample and interpolate first)
    gnss = gnss.reindex(index).interpolate(limit=2, method='time')
    pres = pres.reindex(index).interpolate(limit=2, method='time')
    azim = azim.reindex(index).interpolate(limit=2, method='time')
    tilt = tilt.reindex(index).interpolate(limit=2, method='time')
    tide = tide.reindex(tide.index.union(index)).interpolate(
        limit=2, method='time').reindex(index)

    # concatenate with a multi-index
    return pd.concat(
        [azim, gnss, pres, tilt, tide], axis=1,
        keys=['azim', 'gnss', 'pres', 'tilt', 'tide'],
        names=['variable', 'unit'])


def open_landsat_pairs():
    """Open Landsat velocity pairs with intervals, errors, and speed."""

    # open 2015 images in multi-file dataset
    ds = xr.open_mfdataset(
        '../data/satellite/bowdoin-landsat-uv/*2015_*2015_*.nc',
        combine='nested', combine_attrs='drop_conflicts', concat_dim='time',
        preprocess=lambda ds: ds.assign(title=ds.title.split('/')[-1]))

    # extract intervals and velocity components
    ds = ds.assign(start=xr.DataArray(
        data=pd.to_datetime(ds.title.str[0:8], format='%d%m%Y').values,
        dims='time'))
    ds = ds.assign(end=xr.DataArray(
        data=pd.to_datetime(ds.title.str[9:17], format='%d%m%Y').values,
        dims='time'))
    ds = ds.assign(days=ds.end-ds.start)
    ds = ds.assign(time=ds.start+ds.days/2)
    u = ds.sel(time=ds.title.str.contains('u')).drop_vars('title')
    v = ds.sel(time=ds.title.str.contains('v')).drop_vars('title')
    ds = xr.merge([u.rename(z='u'), v.rename(z='v')], compat='no_conflicts')

    # crop to Bowdoin tongue, select 2015 images, and sort by date
    ds = ds.sel(x=slice(505e3, 515e3), y=slice(8630e3, 8620e3))
    ds = ds.where(ds.time.dt.year == 2015, drop=True).sortby('time').load()

    # estimate error as 0.2 pixel (3 m) over the pair interval, assuming
    # feature-tracking on 15 m Landsat 8 panchromatic images
    # FIXME get a better error estimate from new images
    ds = ds.assign(error=3 * 365 / ds.days.dt.days)

    # compute velocity magnitude
    ds = ds.assign(speed=(ds.u**2+ds.v**2)**0.5)

    # return dataset
    return ds


# Plot methods
# ------------

def add_inset_indicator(ax, inset, connectors=None):
    """Add inset indicator with custom connector visibility.

    The clip_on property is overriden by matplotlib if it detects that some
    other styling properties are the same for the indicator rectangle as for
    the connectors, so we trick matplotlib into believing that the rectangle
    has a different linestyle by using the 'dashed' style for the connectors
    and the matching dashed pattern tuple for the rectangle; this works
    (https://github.com/matplotlib/matplotlib/issues/30642).
    """
    dashes = mpl.rcParams['lines.dashed_pattern']
    indicator = ax.indicate_inset(inset_ax=inset, ls='dashed')
    indicator.rectangle.set_clip_on(True)
    indicator.rectangle.set_clip_box(ax.bbox)
    indicator.rectangle.set_linestyle((0, dashes))
    if connectors is not None:
        for i, connector in enumerate(indicator.connectors):
            connector.set_clip_on(False)
            connector.set_clip_box(ax.figure.bbox)
            connector.set_visible(i in connectors)


def plot_errorbar(ax, df, **kwargs):
    """Plot error bars from dataframe using start, end, and error columns."""
    index = ax.xaxis.get_converter().convert(df.index, None, ax.xaxis)
    xerr = (df.end-df.start)/2/pd.to_timedelta('1'+ax.xaxis.freq)
    return ax.errorbar(
        index, df.speed, xerr=xerr, yerr=df.error,
        linestyle='', linewidth=0.5, zorder=0, **kwargs)


def plot_velocity_quiver(ax, ds, **kwargs):
    """Plot velocity arrows from u and v variables with a 500 m/a key."""
    kwargs = {'color': '0.25', 'scale': 2, 'scale_units': 'x', **kwargs}
    quiver = ds.plot.quiver(
        x='x', y='y', u='u', v='v', ax=ax, add_guide=False, **kwargs)
    ax.quiverkey(
        quiver, 0.85, 0.175, 500, r'500$\,m\,a^{-1}$', color='w',
        labelcolor='w', labelpos='S')
    ax.set_xlabel('')
    ax.set_ylabel('')
    return quiver
