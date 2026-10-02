# Copyright (c) 2015-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Bowdoin deformation paper utils."""

import numpy as np
import pandas as pd
import scipy as sp
import xarray as xr

import bowstr_utils
import bowtem_utils


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


def load_strain(start, end):
    """Load total strain on custom interval."""
    tilx = bowstr_utils.load(variable='tilx')
    tily = bowstr_utils.load(variable='tily')
    tilx = tilx.loc[end].mean() - tilx.loc[start].mean()
    tily = tily.loc[end].mean() - tily.loc[start].mean()
    costilt = np.cos(tilx) * np.cos(tily)
    return 0.5 * (1 - costilt**2) ** 0.5 / costilt


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


def load_multivariate(join='inner', filt=None, method='savgol', window='12h'):
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

# ----------------------------------------------------------------------

# FIXME untested broken code below duplicating bowtem_utils and other projects
# pylint: disable=consider-using-f-string,consider-using-from-import
# pylint: disable=dangerous-default-value,fixme
# pylint: disable=import-error,import-outside-toplevel,invalid-name
# pylint: disable=missing-function-docstring,no-member
# pylint: disable=undefined-variable,unnecessary-negation,unused-argument
# pylint: disable=redefined-outer-name,disable=singleton-comparison
# pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments

# Global parameters
# -----------------

g = 9.80665  # gravitational acceleration in m s-2
COLOURS = {'bh1': 'C0', 'bh2': 'C1', 'bh3': 'C2', 'err': '0.75'}
MARKERS = {'I': '^', 'P': 's', 'T': 'o'}
DRILLING_DATES = {'bh1': '20140716', 'bh2': '20140717', 'bh3': '20140722'}


# Data processing methods
# -----------------------

def longest_continuous(ts):
    """Return longest continuous segment of a data series."""

    # assign group ids to continuous data segments
    groupids = (ts.notnull().shift(1) != ts.notnull()).cumsum()
    groupids[ts.isnull()] = np.nan

    # split groups and select the one with maximum size
    grouped = ts.groupby(groupids)
    longest = grouped.size().idxmax()
    ts = grouped.get_group(longest)
    return ts


# Methods to load borehole data
# -----------------------------

def load_all_depth(borehole):
    """Load all sensor depths in a single dataset."""

    # read depths
    temp_depth = load_depth('thstring', borehole)
    tilt_depth = load_depth('tiltunit', borehole)
    pres_depth = load_depth('pressure', borehole)
    pres_depth.index = ['pres']

    # concatenate datasets
    df = pd.concat((temp_depth, tilt_depth, pres_depth))  # FIXME?
    return df


def load_data(sensor, variable, borehole):
    """Return sensor variable data in a dataframe."""

    # check argument validity
    assert sensor in ('dgps', 'pressure', 'thstring', 'tiltunit')
    assert variable in ('base', 'depth', 'mantemp', 'temp', 'tiltx', 'tilty',
                        'wlev', 'velocity')
    assert borehole in ('both', 'lower', 'upper')

    # read data
    if borehole in ('lower', 'upper'):
        filename = ('../data/processed/bowdoin-%s-%s-%s.csv'
                    % (sensor, variable, borehole))
        df = pd.read_csv(filename, parse_dates=True, index_col='date')
        df = df.groupby(level=0).mean()
    elif borehole == 'both':
        dfu = load_data(sensor, variable, 'upper')
        dfl = load_data(sensor, variable, 'lower')
        df = pd.concat([dfu, dfl], axis=1)
    return df


def load_depth(sensor, borehole):
    """Return sensor depths in a data series."""
    # FIXME: this only read initial depth at the moment

    # read data as a series
    df = load_data(sensor, 'depth', borehole).iloc[0]
    return df


def load_bowtid_depth():
    ts = load_depth('tiltunit', 'both')
    ts = ts.sort_index(ascending=False)
    ts.index = [c[0::3] for c in ts.index]
    ts = ts.drop(['L1', 'L2', 'U1'])
    return ts


def load_total_strain(borehole, start, end=None, as_angle=False):
    """Return horizontal shear strain rate from tilt relative to a start date
    or between two dates."""

    # check argument validity
    assert borehole in ('lower', 'upper')

    # load tilt data
    tiltx = load_data('tiltunit', 'tiltx', borehole)
    tilty = load_data('tiltunit', 'tilty', borehole)

    # compute start and end values
    tx0 = tiltx[start].mean()
    ty0 = tilty[start].mean()
    if end is not None:
        tx1 = tiltx[end].mean()
        ty1 = tilty[end].mean()
    else:
        tx1 = tiltx
        ty1 = tilty

    # compute deformation rate in horizontal plane
    exz_x = np.sin(tx1)-np.sin(tx0)
    exz_y = np.sin(ty1)-np.sin(ty0)
    exz = np.sqrt(exz_x**2+exz_y**2)

    # convert to angles
    if as_angle:
        exz = np.arcsin(exz)*180/np.pi

    # return strain rate
    return exz


# Methods to load external data
# -----------------------------

def load_temp_sigma(site='B'):
    """Return 2014--2016 weather station air temperature in a data series."""

    # list file names
    years = [2014, 2015, 2016, 2017]
    fname = '../data/external/SIGMA_AWS_SiteB_%4d_level0_final.xls'
    files = [fname % y for y in years]

    # open in a data series
    csvkw = {
        'index_col': 0, 'usecols': [0, 3], 'na_values': (-50, -9999),
        'squeeze': True}
    ts = pd.concat([pd.read_excel(f, **csvkw) for f in files])

    # return temperature data series
    return ts


def load_tide_hour():
    """Load GLOSS hourly Pituffik tide data."""

    # date parser
    def parser(index):
        date_str = index[11:-1].replace(' ', '0')
        hour_str = {'1': '00', '2': '12'}[index[-1]]
        return pd.datetime.strptime(date_str+hour_str, '%Y%m%d%H')

    # read data
    skiprows = [0, 245, 976, 1709, 2440, 3171, 3902,
                4635, 5366, 6097, 6828, 7561]
    df = pd.read_fwf('../data/external/h808.dat', skiprows=skiprows,
                     index_col=0, parse_dates=True, date_parser=parser,
                     header=None, delimiter=' ', dtype=None, na_values='9999')

    # stack and reindex
    df = df.stack()
    df.index = df.index.map(lambda x: x[0] + pd.to_timedelta(x[1]-1, unit='H'))

    # convert to meter and remove mean
    df = (df-df.mean())/1e3
    return df


# Methods to open geographic data
# -------------------------------

def open_gtif(filename, extent=None):
    """Open GeoTIFF and return data and extent."""

    # open dataset
    from osgeo import gdal
    ds = gdal.Open(filename)

    # read geotransform
    x0, dx, dxdy, y0, dydx, dy = ds.GetGeoTransform()
    assert dxdy == dydx == 0.0  # rotation parameters should be zero

    # if extent argument was not given
    if extent is None:

        # set image indexes to cover whole image
        col0 = 0  # index of first (W) column
        row0 = 0  # index of first (N) row
        cols = ds.RasterXSize  # number of cols to read
        rows = ds.RasterYSize  # number of rows to read

    # if extent argument was given
    else:

        # compute image indexes corresponding to map extent
        w, e, s, n = extent
        col0 = int((w-x0)/dx)  # index of first (W) column
        row0 = int((n-y0)/dy)  # index of first (N) row
        col1 = int((e-x0)/dx) + 1  # index of last (E) column
        row1 = int((s-y0)/dy) + 1  # index of last (S) row

        # make sure indexes are within data extent
        col0 = max(0, col0)
        row0 = max(0, row0)
        col1 = min(ds.RasterXSize, col1)
        row1 = min(ds.RasterYSize, row1)

        # compute number of cols and rows needed
        cols = col1 - col0  # number of cols needed
        rows = row1 - row0  # number of rows needed

        # compute coordinates of new origin
        x0 = x0 + col0*dx
        y0 = y0 + row0*dy

    # compute new image extent
    x1 = x0 + dx*cols
    y1 = y0 + dy*rows

    # read image data
    data = ds.ReadAsArray(col0, row0, cols, rows)

    # close dataset and return image data and extent
    ds = None
    return data, (x0, x1, y0, y1)


# Axes preparation
# ----------------


def unframe(ax, edges=['bottom', 'left']):
    """Unframe axes to leave only specified edges visible."""

    # remove background patch
    ax.patch.set_visible(False)

    # adjust bounds
    active_spines = [ax.spines[s] for s in edges]
    for s in active_spines:
        s.set_smart_bounds(True)

    # get rid of extra spines
    hidden_spines = [ax.spines[s] for s in ax.spines if s not in edges]
    for s in hidden_spines:
        s.set_visible(False)

    # set ticks positions
    ax.xaxis.set_ticks_position([['none', 'top'], ['bottom', 'both']]
                                ['bottom' in edges]['top' in edges])
    ax.yaxis.set_ticks_position([['none', 'right'], ['left', 'both']]
                                ['left' in edges]['right' in edges])

    # set label positions
    if 'right' in edges and 'left' not in edges:
        ax.yaxis.set_label_position('right')
    if 'top' in edges and 'bottom' not in edges:
        ax.xaxis.set_label_position('top')


# Timeseries elements
# -------------------

def resample_plot(ax, ts, freq, c='b'):
    """Plot resampled mean and std of a timeseries."""
    avg = ts.resample(freq).mean()
    std = ts.resample(freq).std()
    avg.plot(ax=ax, color=c, ls='-')
    # for some reason not working
    ax.fill_between(avg.index, avg-2*std, avg+2*std, color=c, alpha=0.25)


def rolling_plot(ax, ts, window, c='b'):
    """Plot rolling window mean and std of a timeseries."""
    avg = pd.rolling_mean(ts, window)
    std = pd.rolling_std(ts, window)
    avg.plot(ax=ax, color=c, ls='-')
    ax.fill_between(avg.index, avg-2*std, avg+2*std, color=c, alpha=0.25)


# Map elements
# ------------

def shading(z, dx=None, dy=None, extent=None, azimuth=315.0, altitude=30.0,
            transparent=False):
    """Compute shaded relief map."""

    # get horizontal resolution
    if (dx is None or dy is None) and (extent is None):
        raise ValueError("Either dx and dy or extent must be given.")
    rows, cols = z.shape
    dx = dx or (extent[1]-extent[0])/cols
    dy = dy or (extent[2]-extent[3])/rows

    # convert to anti-clockwise rad
    azimuth = -azimuth*np.pi / 180.
    altitude = altitude*np.pi / 180.

    # compute cartesian coords of the illumination direction
    xlight = np.cos(azimuth) * np.cos(altitude)
    ylight = np.sin(azimuth) * np.cos(altitude)
    zlight = np.sin(altitude)

    # for transparent shades set horizontal surfaces to zero
    if transparent is True:
        zlight = 0.0

    # compute hillshade (dot product of normal and light direction vectors)
    u, v = np.gradient(z, dx, dy)
    return (zlight - u*xlight - v*ylight) / (1 + u**2 + v**2)**(0.5)


def slope(z, dx=None, dy=None, extent=None, smoothing=None):
    """Compute slope map with optional smoothing."""

    # get horizontal resolution
    if (dx is None or dy is None) and (extent is None):
        raise ValueError("Either dx and dy or extent must be given.")
    rows, cols = z.shape
    dx = dx or (extent[1]-extent[0])/cols
    dy = dy or (extent[2]-extent[3])/rows

    # optionally smooth data
    if smoothing:
        import scipy.ndimage as ndimage
        z = ndimage.filters.gaussian_filter(z, smoothing)

    # compute gradient along each coordinate
    u, v = np.gradient(z, dx, dy)

    # compute slope
    slope = (u**2 + v**2)**0.5
    return slope


def extent_from_coords(x, y):
    """Compute image extent from coordinate vectors."""
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2
    return w, e, s, n


def coords_from_extent(extent, cols, rows):
    """Compute coordinate vectors from image extent."""

    # compute dx and dy
    (w, e, s, n) = extent
    dx = (e-w) / cols
    dy = (n-s) / rows

    # prepare coordinate vectors
    xwcol = w + 0.5*dx  # x-coord of W row cell centers
    ysrow = s + 0.5*dy  # y-coord of N row cell centers
    x = xwcol + np.arange(cols)*dx  # from W to E
    y = ysrow + np.arange(rows)*dy  # from S to N

    # return coordinate vectors
    return x, y
