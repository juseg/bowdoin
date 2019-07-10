#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature profiles."""

import numpy as np
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


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax0, ax1) = apl.subplots_mm(
        figsize=(150, 75), ncols=2, sharey=True,
        gridspec_kw=dict(left=10, right=2.5, bottom=10, top=2.5, wspace=2.5))

    # add subfigure labels
    util.com.add_subfig_label(ax=ax0, text='(a)', ypad=15)
    util.com.add_subfig_label(ax=ax1, text='(b)', ypad=15)

    # for each borehole
    for bh, color in util.tem.COLOURS.items():

        # load initial temperature profiles
        temp, depth, base = util.tem.load_all(bh)
        dates = util.tem.PROFILES_DATES[bh]
        temp0 = temp[dates[0]].mean()

        # load final profiles ev. using manual data
        try:
            temp1 = temp[dates[1]].mean()
        except KeyError:
            manu, mask = util.tem.load_manual(bh)
            temp1 = manu.mask(mask).loc[dates[1], depth.index].squeeze()

        # plot temperature profiles
        ax0.plot(temp0, depth, c=color, label=bh.upper() + ', ' + dates[0])
        ax0.plot(temp1, depth, c=color, label=bh.upper() + ', ' + dates[1],
                 ls='--', lw=0.5,)
        ax1.plot(temp1-temp0, depth, c=color, ls='--', lw=0.5)

        # plot theroretical diffusion
        dates = pd.to_datetime(dates)
        ax1.plot((dates[1]-dates[0]).total_seconds() *
                 compute_diffusive_heating(depth, temp0), depth, c=color)

        # add markers by sensor type
        for sensor, marker in util.tem.MARKERS.items():
            ax0.plot(temp0[depth.index.str[1] == sensor],
                     depth[depth.index.str[1] == sensor],
                     c=color, marker=marker, ls='', label='')

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
    ax1.set_xlim(-0.3, 0.7)

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
