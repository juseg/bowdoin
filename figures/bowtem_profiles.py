#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature profiles."""

import absplots as apl
import geopandas as gpd
import numpy as np
import pandas as pd
import scipy.interpolate as sinterp

import bowtem_utils


# Physical constants
ACTIV_ENERGY = 115e3    # Flow law act. ener.,  J mol-1         (CP10, p. 74)
CLAPEYRON = 7.9e-8      # Clapeyron constant,   K Pa-1          (LU02)
CAPACITY = 2097         # Ice spec. heat cap.,  J kg-1 K-1      (CP10, p. 400)
CONDUCTIVITY = 2.10     # Ice thermal cond.,    J m-1 K-1 s-1   (CP10, p. 400)
DENSITY = 917           # Ice density,          kg m-3          (CP10, p. 12)
GAS_CONSTANT = 8.314    # Ideal gas constant,   J mol-1 K-1     (CP10, p. 72)
GRAVITY = 9.80665       # Standard gravity,     m s-2           (--)
HARDNESS = 3.5e-25      # Ice hardness coeff.,  Pa-3 s-1        (CP10 p. 74)
LATENT_HEAT = 3.35e5    # Latent heat fusion,   J kg-1 K-1      (CP10, p. 400)

# References
# - CP10: CP10
# - LU02: Lüthi et al., 2002


def compute_ice_hardness(temp, depth):
    """Compute the temperature and depth-dependant ice hardness."""
    melt_pt = compute_melting_point(depth)
    temp_pa = 273.15+temp-melt_pt
    temp_th = 263-melt_pt
    coeff = np.exp(-ACTIV_ENERGY/GAS_CONSTANT*(1/temp_pa-1/temp_th))
    return HARDNESS * coeff


def compute_melting_point(depth):
    """Compute the pressure-melting point from depth below the ice surface."""
    return -CLAPEYRON * DENSITY * GRAVITY * depth


def compute_series_gradient(temp, depth):
    """Compute temperature gradient as a data series."""
    return pd.Series(index=temp.index, data=np.gradient(temp, depth))


def compute_theoretical_crevasse_depth(temp, depth):
    """Compute theoretical crevasse depth."""
    e_xx = estimate_longitudinal_strain_rate()
    hardness = compute_ice_hardness(temp, depth).min()
    return 2/(DENSITY*GRAVITY) * (e_xx / hardness)**(1/3)


def compute_theoretical_diffusion(temp, depth):
    """Compute temperature rate of change by heat diffusion."""
    heat_flux = CONDUCTIVITY * compute_series_gradient(temp, depth)
    return compute_series_gradient(heat_flux, depth)


def compute_theoretical_dissipation(bh, temp, depth):
    """
    Compute theoretical dissipation in Pa s-1 assuming a constrant effective
    strain rate from the evolution of distance between BH1 and BH3 and the
    average shear strain from BH1 and BH3.
    """

    # estimate effective strain rate
    e_xx = estimate_longitudinal_strain_rate()
    e_xz = estimate_shear_strain_rate(bh)
    e_e = (e_xx**2+e_xz**2)**0.5

    # estimate heat dissipation
    hardness = compute_ice_hardness(temp, depth)
    heat = 2 * hardness**(-1/3) * e_e**(4/3)

    # print numbers
    # print(bh.upper())
    # print("long. strain rate:     {:.2e} s-1".format(e_xx))
    # print("shear strain rate:     {:.2e} s-1".format(e_xz))
    # print("effective strain rate: {:.2e} s-1".format(e_e))
    # print("mean heat dissipation: {:.2e} Pa s-1".format(heat.mean()))

    # return temperature change
    return heat


def compute_theoretical_warming(bh, temp, depth):
    """Compute theoretical temperature change in °C a-1 from both heat diffusion
    and viscous dissipation."""
    diffusion = compute_theoretical_diffusion(temp, depth)
    dissipation = compute_theoretical_dissipation(bh, temp, depth)
    return (diffusion + dissipation) / (DENSITY * CAPACITY)


def estimate_longitudinal_strain_rate():
    """
    Estimate longitudinal strain rate from from the evolution of distance
    between BH1 and BH3.
    """

    # open borehole locations
    gdf = gpd.read_file('../data/locations.gpx').set_index('name')
    gdf = gdf.to_crs('+proj=utm +zone=19')

    # compute distance between boreholes
    x = gdf.geometry.x
    y = gdf.geometry.y
    dist_17 = ((x.B17BH3 - x.B17BH1)**2 + (y.B17BH3 - y.B17BH1)**2)**0.5
    dist_14 = ((x.B14BH3 - x.B14BH1)**2 + (y.B14BH3 - y.B14BH1)**2)**0.5

    # compute average time interval
    time = pd.to_datetime(gdf.time, format='mixed', utc=True)
    span = (time.B17BH1 - time.B14BH1 + time.B17BH3 - time.B14BH3)/2

    # estimate longitudinal strain rate
    e_xx = 2 * (dist_17 - dist_14) / (dist_17 + dist_14) / span.total_seconds()
    return e_xx


def estimate_shear_strain_rate(bh):
    """
    Estimate shear strain rate from the average observed tilt rates
    in BH1 and BH3.
    """
    bh = bh.replace('bh2', 'bh1').replace('err', 'bh3')
    e_xz = bowtem_utils.load_strain_rate(bh)['2014-10':].mean()
    e_xz = e_xz.mean()
    return e_xz


def plot_interp(ax, depth, temp, **kwargs):
    """
    Plot spline-interpolated temperature profile.
    """

    # drop isolated points and nans
    temp = temp[temp.shift(-1).notna() | temp.shift(1).notna()].dropna()
    depth = depth[temp.index]

    # interpolate temps to a 1 meter resolution
    depth_new = np.arange(depth.iloc[0], depth.iloc[-1], 1)
    temp_new = sinterp.interp1d(depth, temp, kind='cubic')(depth_new)

    # plot the result
    return ax.plot(temp_new, depth_new, **kwargs)


def plot_markers(ax, depth, temp, **kwargs):
    """
    Plot markers profile based on sensor type.
    """
    for sensor, marker in bowtem_utils.MARKERS.items():
        mask = depth.index.str[1] == sensor
        ax.plot(temp[mask], depth[mask], marker=marker, ls='', **kwargs)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax0, ax1) = apl.subplots_mm(
        figsize=(180, 90), ncols=2, sharey=True, gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=2.5))

    # add subfigure labels
    bowtem_utils.add_subfig_label(ax=ax0, text='(a)')
    bowtem_utils.add_subfig_label(ax=ax1, text='(b)')

    # for each borehole
    for bh, color in bowtem_utils.COLOURS.items():

        # load temperature profiles
        temp, depth, base = bowtem_utils.load_profiles(bh)
        temp0 = temp.iloc[:, 0]
        temp1 = temp.iloc[:, 1]

        # plot markers profile
        plot_markers(ax0, depth, temp0, c=color)

        # plot interpolates between sensors
        for i, date in enumerate(temp):
            plot_interp(ax0, depth, temp[date], c=color,
                        label='{}, {}-{}-{}'.format(
                            bh.upper(), date[:4], date[4:6], date[6:]),
                        ls=('--' if i > 0 else '-'), lw=(0.5 if i > 0 else 1))

        # plot temperature change
        dates = pd.to_datetime(temp.columns)
        change = (temp1-temp0)/((dates[1]-dates[0])/pd.to_timedelta('1s'))
        change *= 60*60*24*365.2425
        plot_interp(ax1, depth, change, c=color)

        # annotate minimum observed temperature below 50m depth
        sensor = temp0[depth > 50].idxmin()
        ax0.text(temp0[sensor], depth[sensor], '%.2f°C  ' % temp0[sensor],
                 color=color, ha='right', va='bottom')

        # annotate maximum observed warming below
        sensor = change.idxmax()
        ax1.plot(change[sensor], depth[sensor], c=color,
                 marker=bowtem_utils.MARKERS[sensor[1]])
        ax1.text(change[sensor], depth[sensor],
                 r'  +%.2f$°C\,a^{-1}$' % (change)[sensor], color=color,
                 ha='left', va='bottom')

        # print theoretical crevasse depth
        # print(bh, compute_theoretical_crevasse_depth(temp0, depth))

        # plot theroretical diffusion
        change = compute_theoretical_warming(bh, temp0, depth)
        change *= 60*60*24*365.2425
        plot_interp(ax1, depth, change, c=color, ls='-.', lw=0.5)

        # add base line
        ax0.axhline(base, color=color, lw=0.5)
        ax1.axhline(base, color=color, lw=0.5)

    # add ice surface
    ax0.axhline(0, color='k', lw=0.5)
    ax1.axhline(0, color='k', lw=0.5)

    # plot melting point and zero line
    ax0.plot([0, compute_melting_point(272)], [0, 272], c='k', ls=':', lw=0.5)
    ax1.plot([0, 0], [0, 272], c='k', ls=':', lw=0.5)

    # set axes properties
    ax0.invert_yaxis()
    ax0.legend(loc='lower left')
    ax0.set_ylabel('initial sensor depth (m)')
    ax0.set_xlabel(u'ice temperature (°C)')
    ax1.set_xlabel(r'temperature change ($°C\,a^{-1}$)')
    ax0.set_xlim(-11.5, 0.5)
    ax1.set_xlim(-0.3, 0.7)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
