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
    """Compute a log strain rate error per sensor, pooled from power-fit
    residuals of mean strain rates in both boreholes."""
    squares, freedom = 0, 0
    for bh, prefix in BOREHOLES:

        # keep frozen time steps with the most common set of valid sensors
        rates = strain.loc[dates[bh]:, strain.columns.str.startswith(prefix)]
        valid = rates.notna()
        sensors = valid[valid.sum(axis=1) >= 3].value_counts().idxmax()
        sensors = pd.Series(sensors, index=valid.columns)
        rates = rates.loc[valid.eq(sensors).all(axis=1), sensors]

        # fit mean strain rates and add up squared log residuals
        mean = rates.mean().to_frame().T
        fits = compute_power_fits(depth, mean).iloc[0]
        residuals = (
            np.log(mean.iloc[0]) - np.log(fits.constant)
            - fits.exponent * np.log(depth[mean.columns]))
        squares += (residuals**2).sum()
        freedom += fits['count'] - 2

    # return pooled standard deviation
    return (squares / freedom)**0.5


def compute_power_fits(depth, strain):
    """Fit power laws strain = constant * depth ** exponent on each row.

    Also return the count, mean and spread (sum of squared deviations) of
    log depths on each row, needed for error propagation.
    """

    # least squares in log space, ignoring missing values on each row
    valid = strain.notna().to_numpy()
    x = np.where(valid, np.log(depth[strain.columns].to_numpy()), 0)
    y = np.where(valid, np.log(strain.to_numpy()), 0)
    count = valid.sum(axis=1)
    sx, sy = x.sum(axis=1), y.sum(axis=1)
    sxx, sxy = (x*x).sum(axis=1), (x*y).sum(axis=1)
    exponent = (count*sxy - sx*sy) / (count*sxx - sx**2)
    constant = np.exp((sy - exponent*sx) / count)

    # return as dataframe
    return pd.DataFrame({
        'exponent': exponent, 'constant': constant, 'count': count,
        'center': sx/count, 'spread': sxx - sx**2/count}, index=strain.index)


def compute_shear_profile(base, depth, exponent, surface):
    """Compute horizontal shear profile from exponent and surface velocity."""
    return surface * (1 - (depth/base)**(exponent+1))


def compute_shear_series(strain, depth, base, sigma):
    """Compute shear velocity and flow exponent from strain rate profiles,
    and their errors from a constant log strain rate error per sensor."""
    shear, exponent, shear_error, exponent_error = {}, {}, {}, {}
    for bh, prefix in BOREHOLES:

        # fit a power law strain = constant * depth ** exponent at each time
        rates = strain.loc[:, strain.columns.str.startswith(prefix)]
        rates = rates.dropna(how='all')
        fits = compute_power_fits(depth, rates)
        exponent[bh] = fits.exponent

        # integrate strain rate over ice thickness
        thickness = base[f'{bh}B']
        power = fits.exponent + 1
        shear[bh] = 2 * fits.constant / power * thickness**power

        # propagate errors to the exponent and log shear, where the lever is
        # the derivative of log shear with exponent at the mean log depth
        lever = np.log(thickness) - fits.center - 1/power
        exponent_error[bh] = sigma / fits.spread**0.5
        shear_error[bh] = shear[bh] * sigma * (
            1/fits['count'] + lever**2/fits.spread)**0.5

    # return as dataframe with variable and borehole column levels
    return pd.concat({
        'shear': pd.DataFrame(shear), 'exponent': pd.DataFrame(exponent),
        'shear_error': pd.DataFrame(shear_error),
        'exponent_error': pd.DataFrame(exponent_error)}, axis=1)


def plot_faded(ax, df, dates, errors):
    """Plot dataframe columns with error bands, faded before given dates."""
    for bh, series in df.items():
        series[:dates[bh]].plot(
            ax=ax, alpha=0.25, color=COLORS[bh], label='_nolegend_')
        series[dates[bh]:].plot(ax=ax, color=COLORS[bh])

        # add error bands (convert dates as pandas may use periods)
        converter = ax.xaxis.get_converter()
        for part, alpha in [(slice(None, dates[bh]), 0.1),
                            (slice(dates[bh], None), 0.25)]:
            values, error = series[part], errors[bh][part]
            ax.fill_between(
                converter.convert(values.index, None, ax.xaxis),
                values-error, values+error, color=COLORS[bh], alpha=alpha,
                linewidth=0)


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
    """Plot surface speed, shear, slip ratio and flow exponent series."""

    # load surface speed and compute ratio where it intersects shear
    speed = bowdef_utils.load_gnss_velocities(method='kernel', window='3h').vh
    index = series.index.intersection(speed.index)
    ratio = 100 - 100 * series.shear.divide(speed, axis=0).reindex(index)
    ratio_error = 100 * series.shear_error.divide(
        speed, axis=0).reindex(index)

    # plot surface speed, shear and slip ratio from geopositioning
    speed.plot(ax=axes[0], color='tab:orange', label='GNSS')
    plot_faded(axes[1], series.shear, dates, series.shear_error)
    plot_faded(axes[2], ratio, dates, ratio_error)
    plot_faded(axes[3], series.exponent, dates, series.exponent_error)
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


def plot_shear_profiles(axes, rates, depth, base, sigma, summer):
    """Plot shear profiles from power-law fits of window-mean strain rates."""

    # fit power laws to strain rates averaged over the window
    fits = compute_shear_series(
        rates.mean().to_frame().T, depth, base, sigma).iloc[0]
    colors = pd.Series([f'C{i}' for i in range(depth.size)], index=depth.index)

    # plot continuous and discrete profiles in each borehole
    for ax, (bh, prefix) in zip(axes, BOREHOLES):
        units = rates.loc[:, rates.columns.str.startswith(prefix)].dropna(
            axis=1, how='all').columns
        depth_int = np.linspace(0, base[f'{bh}B'], 51)
        shear_int = compute_shear_profile(
            base[f'{bh}B'], depth_int, fits.exponent[bh], fits.shear[bh])
        unit_shear = compute_shear_profile(
            base[f'{bh}B'], depth[units], fits.exponent[bh], fits.shear[bh])
        if summer:
            ax.fill_betweenx(
                depth_int, 0, shear_int, color=COLORS[bh], alpha=0.25)
            ax.plot([0, shear_int[0]], [0, 0], color=COLORS[bh])
        ax.plot(shear_int, depth_int, color=COLORS[bh],
                ls='-' if summer else '--')
        ax.scatter(unit_shear, depth[units], c=colors[units],
                   edgecolors=COLORS[bh], zorder=3)
        if not summer:
            plot_shear_profile_arrows(
                ax, depth[units], unit_shear, color=COLORS[bh])
        ax.text(
            0.05, 0.05 + 0.08 * summer,
            f'{rates.index[0]:%b.} n = {fits.exponent[bh]:.2f} '
            f'± {fits.exponent_error[bh]:.2f}',
            color=COLORS[bh], transform=ax.transAxes)


def main():
    """Main program called during execution."""

    # initialize figure (disable sharex on pfaxes as pandas handle_shared_axes
    # otherwise detect them as sharing axes with the timeseries)
    fig = apl.figure_mm(figsize=(180, 120))
    tsaxes = fig.subplots_mm(nrows=4, sharex=True, gridspec_kw={
        'left': 12.5, 'right': 47.5, 'bottom': 12.5, 'top': 2.5,
        'hspace': 2.5})
    pfaxes = fig.subplots_mm(nrows=2, sharey=True, gridspec_kw={
        'left': 135, 'right': 12.5, 'bottom': 12.5, 'top': 2.5, 'hspace': 2.5})

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
    print(f'pooled log strain rate error per sensor: {sigma:.3f}')
    plot_time_series(
        tsaxes, compute_shear_series(strain, depth, base, sigma), dates)

    # share profile x axes only after pandas plotting (see above)
    pfaxes[1].sharex(pfaxes[0])

    # plot winter and summer shear profiles with borehole labels
    for start, end, summer in WINDOWS:
        plot_shear_profiles(
            pfaxes, strain[start:end], depth, base, sigma, summer)
    for ax, (bh, _) in zip(pfaxes, BOREHOLES):
        ax.text(0.05, 0.21, bh, color=COLORS[bh], fontweight='bold',
                transform=ax.transAxes)

    # set time axes properties
    tsaxes[0].legend(loc='upper right', bbox_to_anchor=(0, 0, 0.94, 1))
    tsaxes[2].legend(loc='upper right', bbox_to_anchor=(0, 0, 0.94, 1))
    tsaxes[3].set_xlabel('')
    tsaxes[0].set_ylabel(r'surface ($m\,a^{-1}$)', labelpad=0)
    tsaxes[1].set_ylabel(r'shear ($m\,a^{-1}$)')
    tsaxes[2].set_ylabel('slip ratio (%)')
    tsaxes[3].set_ylabel('flow exponent', labelpad=8)
    tsaxes[0].set_xlim('20140701', '20170801')
    tsaxes[1].set_ylim(5, 55)
    tsaxes[2].set_ylim(92.5, 97.5)
    tsaxes[3].set_ylim(-0.5, 4.5)

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
