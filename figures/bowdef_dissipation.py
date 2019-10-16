#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Estimate viscous dissipation due to strain heating."""

import pandas as pd
import cartopy.crs as ccrs
import absplots as apl
import util


def main(capacity=2097, density=910.0, hardness=3.5e-25):
    """Main program called during execution."""

    # load borehole positions
    # FIXME allow ccrs as string in read_locations
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
    change = heat / (density * capacity) * 365.25*24*3600

    # output numbers on a figure
    fig = apl.figure_mm(figsize=(85, 30))
    fig.text(0.1, 0.2, (
        "long. strain rate: {:.2e} s-1\n"
        "shear strain rate: {:.2e} s-1\n"
        "effective strain rate: {:.2e} s-1\n"
        "heat dissipation: {:.2e} Pa s-1\n\n"
        "temperature change: {:.2e} °C a-1").format(
            e_xx, e_xz, e_e, heat, change))
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
