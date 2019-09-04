#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature profiles."""

import numpy as np
import scipy.interpolate as sinterp
import pandas as pd
import absplots as apl
import util


def compute_diffusive_heating(depth, temp, capacity=2009, conductivity=2.1,
                              density=910.0):
    """
    Compute temperature rate of change by heat diffusion.

    Parameters
    ----------
    depth : array
        Depth below the ice surface in m.
    temp : array
        Ice temperature in K.
    capacity : scalar
        Ice specific heat capacity in J kg-1 K-1.
    conductivity : scalar
        Ice thermal conductivity in J m-1 K-1 s-1.
    density : scalar
        Ice density in kg m-3.
    """
    heat_flux = conductivity * np.gradient(temp, depth)
    return np.gradient(heat_flux, depth) / (density * capacity)


def compute_melting_point(depth, beta=7.9e-8, gravity=9.80665, rho_i=910.0):
    """
    Compute the pressure-melting point from depth below the ice surface.

    Parameters
    ----------
    depth : scalar
        Depth below the ice surface.
    beta : scalar
        Clapeyron constant for ice (default: Luethi et al., 2002).
    gravity : scalar
        Standard gravity in m s-2.
    rho_i : scalar
        Ice density in kg m-3.
    """
    return -beta * rho_i * gravity * depth


def plot_interp(ax, depth, temp, **kwargs):
    """
    Plot spline-interpolated temperature profile.
    """
    mask = np.isnan(temp)
    temp = temp[~mask]  # pandas equiv. temp.dropna()
    depth = depth[~mask]  # pandas equiv. depth[temp.index]
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
        labels = [bh.upper() + ', ' + date for date in temp]
        plot_interp(ax0, depth, temp0, c=color, label=labels[0])
        plot_interp(ax0, depth, temp1, c=color, label=labels[1], ls='--', lw=0.5)
        plot_interp(ax1, depth, temp1-temp0, c=color, ls='--', lw=0.5)

        # annotate minimum observed temperature below 50m depth
        sensor = temp0[depth > 50].idxmin()
        ax0.text(temp0[sensor], depth[sensor], '%.2f°C  ' % temp0[sensor],
                 color=color, ha='right', va='bottom')

        # annotate maximum observed warming
        sensor = (temp1-temp0).idxmax()
        ax1.plot((temp1-temp0)[sensor], depth[sensor], c=color,
                 marker=util.tem.MARKERS[sensor[1]])
        ax1.text((temp1-temp0)[sensor], depth[sensor],
                 '  +%.2f°C' % (temp1-temp0)[sensor], color=color,
                 ha='left', va='bottom')

        # plot theroretical diffusion
        dates = pd.to_datetime(temp.columns)
        dheat = compute_diffusive_heating(depth, temp0)
        dheat *= (dates[1]-dates[0]).total_seconds()
        ax1.plot(dheat, depth, c=color, marker='_', ls='')
        plot_interp(ax1, depth, dheat, c=color)

        # add base line
        for ax in (ax0, ax1):
            ax.axhline(base, color=color, lw=0.5)

    # add ice surface
    for ax in (ax0, ax1):
        ax.axhline(0, color='k', lw=0.5)

    # plot melting point and zero line
    base = 272
    melt = compute_melting_point(base)
    ax0.plot([0, melt], [0, base], c='k', ls=':', lw=0.5)
    ax1.plot([0, 0], [0, base], c='k', ls=':', lw=0.5)

    # set axes properties
    ax0.invert_yaxis()
    ax0.legend(loc='lower left')
    ax0.set_ylabel('initial sensor depth (m)')
    ax0.set_xlabel(u'ice temperature (°C)')
    ax1.set_xlabel(u'temperature change (°C)')
    ax0.set_xlim(-10.5, 0.5)
    ax1.set_xlim(-0.3, 0.9)

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
