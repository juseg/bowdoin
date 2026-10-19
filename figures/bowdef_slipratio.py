#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin surface and shear velocities and slip ratio."""

import absplots as apl
import matplotlib as mpl
import numpy as np
import pandas as pd

import bowdef_utils
import bowstr_utils
import bowtem_utils
from bowdef_utils import BOREHOLES, COLORS, WINDOWS


def compute_residual_error(strain, depth, dates):
    """Compute a strain rate error per sensor, pooled from linear-fit
    residuals of mean strain rates in both boreholes."""
    squares, freedom = 0, 0
    for bh, prefix in BOREHOLES:

        # keep frozen time steps with the most common set of valid sensors
        rates = strain.loc[dates[bh]:, strain.columns.str.startswith(prefix)]
        valid = rates.notna()
        sensors = valid[valid.sum(axis=1) >= 3].value_counts().idxmax()
        sensors = pd.Series(sensors, index=valid.columns)
        rates = rates.loc[valid.eq(sensors).all(axis=1), sensors]

        # fit mean strain rates and add up squared residuals
        mean = rates.mean().to_frame().T
        fits = compute_linear_fits(depth, mean).iloc[0]
        residuals = (
            mean.iloc[0] - fits.intercept - fits.slope * depth[mean.columns])
        squares += (residuals**2).sum()
        freedom += fits['count'] - 2

    # return pooled standard deviation
    return (squares / freedom)**0.5


def compute_linear_fits(depth, strain):
    """Fit lines strain = intercept + slope * depth on each row.

    Also return the count, mean and spread (sum of squared deviations) of
    depths on each row, needed for error propagation.
    """

    # least squares in centred form, ignoring missing values on each row
    depths = strain*0 + depth[strain.columns]
    center = depths.mean(axis=1)
    deviations = depths.sub(center, axis=0)
    spread = (deviations**2).sum(axis=1)
    slope = (deviations*strain).sum(axis=1) / spread

    # return as dataframe
    return pd.DataFrame({
        'slope': slope, 'intercept': strain.mean(axis=1) - slope*center,
        'count': strain.count(axis=1), 'center': center, 'spread': spread})


def compute_shear_profile(fit, depth, thickness):
    """Compute shear velocity profile from fit parameters, as twice the
    strain rate, clipped at zero, integrated from depth to the bed."""

    # find the segment between depth and the bed where strain rate is positive
    with np.errstate(divide='ignore', invalid='ignore'):
        zero = -fit.intercept / fit.slope
    upper = np.where(fit.slope > 0, np.clip(zero, depth, thickness), depth)
    lower = np.where(fit.slope < 0, np.clip(zero, depth, thickness), thickness)

    # integrate strain rate over the segment, from its midpoint value
    middle = (upper + lower) / 2
    return 2 * (lower-upper) * np.maximum(fit.intercept + fit.slope*middle, 0)


def compute_shear_series(strain, depth, base, sigma):
    """Compute shear velocity from clipped linear fits of strain rate
    profiles, and shear errors from a constant strain rate error per
    sensor."""
    shear, intercept, slope, shear_error, count = {}, {}, {}, {}, {}
    for bh, prefix in BOREHOLES:

        # fit a line strain = intercept + slope * depth at each time
        rates = strain.loc[:, strain.columns.str.startswith(prefix)]
        rates = rates.dropna(how='all')
        fits = compute_linear_fits(depth, rates)
        intercept[bh] = fits.intercept
        slope[bh] = fits.slope
        count[bh] = fits['count']

        # integrate strain rate clipped at zero over ice thickness
        thickness = base[f'{bh}B']
        shear[bh] = pd.Series(
            compute_shear_profile(fits, 0, thickness), index=fits.index)

        # propagate errors to shear, which varies with the fitted strain rate
        # at the midpoint of the positive segment, as both segment ends have
        # zero strain rate or are fixed
        with np.errstate(divide='ignore', invalid='ignore'):
            zero = -fits.intercept / fits.slope
        upper = np.where(fits.slope > 0, np.clip(zero, 0, thickness), 0)
        lower = np.where(
            fits.slope < 0, np.clip(zero, 0, thickness), thickness)
        lever = (upper + lower) / 2 - fits.center
        shear_error[bh] = 2 * (lower-upper) * sigma * (
            1/fits['count'] + lever**2/fits.spread)**0.5

    # return as dataframe with variable and borehole column levels
    return pd.concat({
        'shear': pd.DataFrame(shear), 'intercept': pd.DataFrame(intercept),
        'slope': pd.DataFrame(slope),
        'shear_error': pd.DataFrame(shear_error),
        'count': pd.DataFrame(count)}, axis=1)


def is_solid(series, bh, dates, count):
    """Return where a series follows closure and fits rely on three units."""
    return (series.index >= dates[bh]) & (
        count[bh].reindex(series.index) >= 3)


def plot_faded(ax, df, dates, count):
    """Plot dataframe columns with faded records before given dates and
    where fits rely on less than three units."""
    for bh, series in df.items():
        solid = is_solid(series, bh, dates, count)
        series.where(~solid).plot(
            ax=ax, alpha=0.25, color=COLORS[bh], label='_nolegend_')
        series.where(solid).plot(ax=ax, color=COLORS[bh])


def plot_level_errors(ax, df, dates, count, errors):
    """Plot median values and errors of solid records near the right edge,
    as errors are mostly systematic and change only with sensor sets."""
    for i, (bh, series) in enumerate(df.items()):
        solid = is_solid(series, bh, dates, count)
        ax.errorbar(
            0.976+0.012*i, series[solid].median(),
            yerr=errors[bh][solid].median(), color=COLORS[bh],
            marker='o', markersize=2, capsize=1, linewidth=1, clip_on=False,
            transform=ax.get_yaxis_transform())


def plot_satellite_series(axes, shear, shear_error):
    """Plot surface speed and slip ratio from satellite image pairs."""

    # load velocities from landsat and sentinel images
    landsat = bowdef_utils.load_landsat_velocities()
    sentinel = bowdef_utils.load_sentinel_velocities()
    sat = pd.concat([landsat, sentinel])

    # compute slip ratio from satellite and propagate uncertainties (shear
    # errors are systematic, hence averaged rather than added in quadrature)
    sat_shear = sat.apply(
        lambda row: shear[row.start:row.end].mean(), axis=1)
    sat_shear_error = sat.apply(
        lambda row: shear_error[row.start:row.end].mean(), axis=1)
    sat_speed = 100 - 100 * sat_shear.divide(sat.speed, axis=0)
    sat_error = 100 * sat_shear.multiply(
        1/(sat.speed-sat.error/2)-1/(sat.speed+sat.error/2), axis=0)
    sat_error = (sat_error**2 + (100 * sat_shear_error.divide(
        sat.speed, axis=0))**2)**0.5

    # plot surface speed and slip ratio from satellite
    tab20 = mpl.color_sequences['tab20']
    bowdef_utils.plot_errorbar(
        axes[0], landsat, color=tab20[3], label='Landsat-8')
    bowdef_utils.plot_errorbar(
        axes[0], sentinel, color=tab20[11], label='Sentinel-1')
    for bh, color in [('BH1', tab20[1]), ('BH3', tab20[13])]:
        bowdef_utils.plot_errorbar(axes[1], sat.assign(
            speed=sat_speed[bh], error=sat_error[bh]), color=color)


def plot_time_series(axes, series, dates):
    """Plot surface speed, shear and slip ratio series."""

    # load surface speed and compute ratio where it intersects shear
    speed = bowdef_utils.load_gnss_velocities(method='kernel', window='3h').vh
    index = series.index.intersection(speed.index)
    ratio = 100 - 100 * series.shear.divide(speed, axis=0).reindex(index)
    ratio_error = 100 * series.shear_error.divide(
        speed, axis=0).reindex(index)

    # plot surface speed, shear and slip ratio from geopositioning
    speed.plot(ax=axes[0], color='tab:orange', label='GNSS')
    count = series['count']
    plot_faded(axes[1], series.shear, dates, count)
    plot_faded(axes[2], ratio, dates, count)
    plot_level_errors(
        axes[1], series.shear, dates, count, series.shear_error)
    plot_level_errors(axes[2], ratio, dates, count, ratio_error)
    for ax in axes:
        bowtem_utils.add_field_campaigns(ax=ax, color='0.75')

    # mark profile windows and plot satellite data
    plot_satellite_series(axes[[0, 2]], series.shear, series.shear_error)
    plot_window_indicators(axes[1], series.shear)


def plot_window_indicators(ax, shear):
    """Mark profile windows and mean surface shear velocities."""
    converter = ax.xaxis.get_converter()
    for start, end, _ in WINDOWS:
        surfaces = shear[start:end].mean()
        x0, x1 = converter.convert(
            pd.to_datetime([start, end]), None, ax.xaxis)
        y0, y1 = surfaces.min() - 5, surfaces.max() + 5
        ax.indicate_inset(bounds=[x0, y0, x1-x0, y1-y0], ls='dashed', zorder=5)


def plot_shear_profile_arrows(ax, depth, shear, color='C0'):
    """Draw dashed arrows from the zero axis to tilt units."""
    for unit in depth.index[shear > 5]:  # skip arrows too short for a head
        arrowprops = {
            'color': color, 'clip_box': ax.bbox, 'clip_on': True,
            'shrinkB': 4}

        # draw a dashed tail ending inside the head, and a solid head
        ax.annotate(
            '', xy=(shear[unit], depth[unit]), xytext=(0, depth[unit]),
            zorder=2, arrowprops={
                **arrowprops, 'arrowstyle': '-', 'linestyle': 'dashed',
                'linewidth': 1, 'shrinkB': 6})
        ax.annotate(
            '', xy=(shear[unit], depth[unit]), xytext=(8, 0),
            textcoords='offset points', zorder=2, arrowprops={
                **arrowprops, 'arrowstyle': '-|>', 'linewidth': 1,
                'shrinkA': 0})


def plot_shear_profiles(ax, bh, fits, units, thickness):
    """Plot winter and summer shear profiles in one borehole from clipped
    linear fits of window-mean strain rates (one row per window)."""
    depth_int = np.linspace(0, thickness, 51)
    for (start, _, summer), (_, fit) in zip(WINDOWS, fits.iterrows()):

        # plot continuous and discrete profiles
        shear_int = compute_shear_profile(fit[:, bh], depth_int, thickness)
        unit_shear = pd.Series(compute_shear_profile(
            fit[:, bh], units.depth, thickness), index=units.index)
        if summer:
            ax.fill_betweenx(
                depth_int, 0, shear_int, color=COLORS[bh], alpha=0.25)
            ax.plot([0, shear_int[0]], [0, 0], color=COLORS[bh])
        ax.plot(shear_int, depth_int, color=COLORS[bh],
                ls='-' if summer else '--')
        ax.scatter(unit_shear, units.depth, c=units.color,
                   edgecolors=COLORS[bh], zorder=3)
        if not summer:
            plot_shear_profile_arrows(
                ax, units.depth, unit_shear, color=COLORS[bh])

        # mark surface shear errors just below the surface
        ax.errorbar(
            fit.shear[bh], 12 + 12*summer, xerr=fit.shear_error[bh],
            color=COLORS[bh], marker='o', markersize=3, capsize=1.5,
            linewidth=1, markerfacecolor=COLORS[bh] if summer else 'w')
        ax.text(
            0.05, 0.05 + 0.1 * summer,
            f'{pd.Timestamp(start):%b.} {fit.shear[bh]:.1f}'
            r'$\,m\,a^{-1}$', color=COLORS[bh], transform=ax.transAxes)

    # add borehole label
    ax.text(0.05, 0.25, bh, color=COLORS[bh], fontweight='bold',
            transform=ax.transAxes)


def main():
    """Main program called during execution."""

    # initialize figure (disable sharex on pfaxes as pandas handle_shared_axes
    # otherwise detect them as sharing axes with the timeseries)
    fig = apl.figure_mm(figsize=(180, 90))
    tsaxes = fig.subplots_mm(nrows=3, sharex=True, gridspec_kw={
        'left': 12.5, 'right': 47.5, 'bottom': 10, 'top': 2.5, 'hspace': 2.5})
    pfaxes = fig.subplots_mm(nrows=2, sharey=True, gridspec_kw={
        'left': 135, 'right': 12.5, 'bottom': 10, 'top': 2.5, 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels([*tsaxes, *pfaxes])

    # load sensor depths, ice thickness and strain rates
    base = bowstr_utils.load(variable='base').iloc[0]
    depth = bowstr_utils.load(variable='dept').iloc[0]
    strain = bowdef_utils.load_strain_rates(method='kernel', window='3h')

    # load latest freezing date in each borehole
    dates = bowstr_utils.load_freezing_dates()
    dates = dates.groupby(dates.index.str[0]).max()
    dates = dates.rename({'L': 'BH3', 'U': 'BH1'})

    # estimate strain rate errors and plot time series
    sigma = compute_residual_error(strain, depth, dates)
    print(f'pooled strain rate error per sensor: {sigma:.4f} a-1')
    plot_time_series(
        tsaxes, compute_shear_series(strain, depth, base, sigma), dates)

    # share profile x axes only after pandas plotting (see above)
    pfaxes[1].sharex(pfaxes[0])

    # fit lines to strain rates averaged over each window
    means = pd.DataFrame([strain[start:end].mean() for start, end, _ in WINDOWS])
    fits = compute_shear_series(means, depth, base, sigma)

    # plot winter and summer shear profiles, coloring units as in other plots
    units = pd.DataFrame({
        'depth': depth, 'color': [f'C{i}' for i in range(depth.size)]})
    for ax, (bh, prefix) in zip(pfaxes, BOREHOLES):
        active = means.columns.str.startswith(prefix) & means.notna().all()
        plot_shear_profiles(
            ax, bh, fits, units.loc[means.columns[active]], base[f'{bh}B'])

    # set time axes properties
    tsaxes[0].legend(loc='upper right', bbox_to_anchor=(0, 0, 0.94, 1))
    tsaxes[2].legend(loc='upper right', bbox_to_anchor=(0, 0, 0.94, 1))
    tsaxes[2].set_xlabel('')
    tsaxes[0].set_ylabel(r'surface ($m\,a^{-1}$)', labelpad=0)
    tsaxes[1].set_ylabel(r'shear ($m\,a^{-1}$)')
    tsaxes[2].set_ylabel('slip ratio (%)')
    tsaxes[0].set_xlim('20140701', '20170801')
    tsaxes[1].set_ylim(5, 55)
    tsaxes[2].set_ylim(92.5, 97.5)

    # set profile axes properties
    pfaxes[1].set_xlabel(r'shear ($m\,a^{-1}$)')
    pfaxes[0].tick_params(labelbottom=False)
    for ax in pfaxes:
        ax.set_ylabel('depth (m)')
        ax.set_xlim(30, 0)
        ax.set_ylim(315, -15)
        ax.yaxis.set_label_position('right')
        ax.yaxis.tick_right()

    # set common axes properties
    for ax in [*tsaxes, *pfaxes]:
        ax.grid(which='minor')

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
