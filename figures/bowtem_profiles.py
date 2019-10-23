#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature profiles."""

import numpy as np
import scipy.interpolate as sinterp
import pandas as pd
import cartopy.crs as ccrs
import absplots as apl
import util


def compute_melting_point(depth, clapeyron=util.com.CLAPEYRON,
                          density=util.com.DENSITY, gravity=util.com.GRAVITY):
    """
    Compute the pressure-melting point from depth below the ice surface.

    Parameters
    ----------
    depth : scalar
        Depth below the ice surface.
    clapeyron : scalar
        Clapeyron constant for ice.
    density : scalar
        Ice density in kg m-3.
    gravity : scalar
        Standard gravity in m s-2.
    """
    return -clapeyron * density * gravity * depth


def compute_series_gradient(temp, depth):
    """Compute temperature gradient as a data series."""
    temp[:] = np.gradient(temp, depth)
    return temp


def compute_theoretical_diffusion(temp, depth, capacity=util.com.CAPACITY,
                                  conductivity=util.com.CONDUCTIVITY,
                                  density=util.com.DENSITY):
    """
    Compute temperature rate of change by heat diffusion.

    Parameters
    ----------
    temp : array
        Ice temperature in K.
    depth : array
        Depth below the ice surface in m.
    capacity : scalar
        Ice specific heat capacity in J kg-1 K-1.
    conductivity : scalar
        Ice thermal conductivity in J m-1 K-1 s-1.
    density : scalar
        Ice density in kg m-3.
    """
    heat_flux = conductivity * compute_series_gradient(temp, depth)
    return compute_series_gradient(heat_flux, depth) / (density * capacity)


def compute_theoretical_dissipation(capacity=util.com.CAPACITY,
                                    density=util.com.DENSITY,
                                    hardness=util.com.HARDNESS):
    """Main program called during execution."""

    # load borehole positions
    locs = util.com.read_locations(crs=ccrs.UTM(19))
    d_17 = ((locs.x.B17BH3-locs.x.B17BH1)**2 +
            (locs.y.B17BH3-locs.y.B17BH1)**2)**0.5
    d_14 = ((locs.x.B14BH3-locs.x.B14BH1)**2 +
            (locs.y.B14BH3-locs.y.B14BH1)**2)**0.5
    time = (locs.time.B17BH1 - locs.time.B14BH1 +
            locs.time.B17BH3 - locs.time.B14BH3)/2

    # estimate effective strain rate
    e_xx = 2*(d_17-d_14)/(d_17+d_14)/time.total_seconds()
    e_xz = pd.concat([util.inc.load_strain_rate(bh)['2014-10':].mean()
                      for bh in ('bh1', 'bh3')]).mean()
    e_e = (e_xx**2+e_xz**2)**0.5

    # estimate heat dissipation
    # FIXME ice hardness depends on temperature
    heat = 2 * hardness**(-1/3)*e_e**(4/3)

    # estimate temperature change
    change = heat / (density * capacity)

    # print numbers
    # print("long. strain rate:     {:.2e} s-1".format(e_xx))
    # print("shear strain rate:     {:.2e} s-1".format(e_xz))
    # print("effective strain rate: {:.2e} s-1".format(e_e))
    # print("heat dissipation:      {:.2e} Pa s-1".format(heat))
    # s2a = pd.to_timedelta('1Y') / pd.to_timedelta('1S')
    # print("temperature change:    {:.2e} °C a-1".format(change*s2a))

    # return temperature change
    return change


def compute_theoretical_warming(temp, depth, capacity=util.com.CAPACITY,
                                conductivity=util.com.CONDUCTIVITY,
                                density=util.com.DENSITY,
                                hardness=util.com.HARDNESS):
    """
    Compute theoretical temperature change in °C a-1 from both heat diffusion
    and viscous dissipation.
    """
    diffusion = compute_theoretical_diffusion(temp, depth, capacity=capacity,
                                              conductivity=conductivity,
                                              density=density)
    dissipation = compute_theoretical_dissipation(capacity=capacity,
                                                  density=density,
                                                  hardness=hardness)
    print(diffusion)
    print(dissipation)
    return diffusion + dissipation


def plot_interp(ax, depth, temp, **kwargs):
    """
    Plot spline-interpolated temperature profile.
    """
    temp = temp.dropna()
    depth = depth[temp.index]
    depth_new = np.arange(depth[0], depth[-1], 1)
    temp_new = sinterp.interp1d(depth, temp, kind='cubic')(depth_new)
    return ax.plot(temp_new, depth_new, **kwargs)


def plot_markers(ax, depth, temp, **kwargs):
    """
    Plot markers profile based on sensor type.
    """
    for sensor, marker in util.tem.MARKERS.items():
        mask = depth.index.str[1] == sensor
        ax.plot(temp[mask], depth[mask], marker=marker, ls='', **kwargs)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax0, ax1) = apl.subplots_mm(
        figsize=(180, 90), ncols=2, sharey=True, gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=2.5))

    # add subfigure labels
    util.com.add_subfig_label(ax=ax0, text='(a)', ypad=15)
    util.com.add_subfig_label(ax=ax1, text='(b)', ypad=15)

    # for each borehole
    for bh, color in util.tem.COLOURS.items():

        # load temperature profiles
        temp, depth, base = util.tem.load_profiles(bh)
        temp0 = temp.iloc[:, 0]
        temp1 = temp.iloc[:, 1]

        # plot markers profile
        plot_markers(ax0, depth, temp0, c=color)

        # plot interpolates between sensors
        plot_interp(ax0, depth, temp0, c=color,
                    label=bh.upper() + ', ' + temp0.name)
        plot_interp(ax0, depth, temp1, c=color,
                    label=bh.upper() + ', ' + temp1.name, ls='--', lw=0.5)

        # plot temperature change
        dates = pd.to_datetime(temp.columns)
        change = (temp1-temp0)/((dates[1]-dates[0])/pd.to_timedelta('1Y'))
        plot_interp(ax1, depth, change, c=color, ls='--', lw=0.5)

        # annotate minimum observed temperature below 50m depth
        sensor = temp0[depth > 50].idxmin()
        ax0.text(temp0[sensor], depth[sensor], '%.2f°C  ' % temp0[sensor],
                 color=color, ha='right', va='bottom')

        # annotate maximum observed warming below
        sensor = change.idxmax()
        ax1.plot(change[sensor], depth[sensor], c=color,
                 marker=util.tem.MARKERS[sensor[1]])
        ax1.text(change[sensor], depth[sensor],
                 r'  +%.2f$°C\,a^{-1}$' % (change)[sensor], color=color,
                 ha='left', va='bottom')

        # plot theroretical diffusion
        change = compute_theoretical_warming(temp0, depth)
        change *= pd.to_timedelta('1Y') / pd.to_timedelta('1S')
        ax1.plot(change, depth, c=color, marker='_', ls='')
        plot_interp(ax1, depth, change, c=color)

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
    ax0.set_xlim(-10.5, 0.5)
    ax1.set_xlim(-0.3, 0.9)

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
