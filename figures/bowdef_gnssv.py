#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation against GNSS velocity."""

import absplots as apl
import numpy as np
import pandas as pd
import pyproj
import scipy

import bowstr_utils
import bowtem_utils


def read_gnss_velocities(borehole=1):
    """Compute velocity components from raw data of one station."""
    # FIXME duplicates preprocessing code, also this function is a mess, seems
    # to include multiple ways to compute the derivatives

    # read gps data
    df = pd.read_fwf(
        # f"../data/external.bkp/gps/B16{borehole:02d}_15min.dat",
        "../data/original/gps/B14BH1/B14BH1_2016_15min.dat",
        names=[
            "daydate", "time", "lat", "lon", "z", "Q", "ns", "sdn", "sde",
            "sdu", "sdne", "sdeu", "sdun", "age", "ratio"],
        index_col=0,
        usecols=["daydate", "time", "lon", "lat", "z"],
        parse_dates={"date": ["daydate", "time"]},
    )

    # find samples not taken at multiples of 15 min (900 sec) and remove them
    # it seems these (18) values were recorded directly after each data gap
    # FIXME is this still needed now?
    inpace = (60 * df.index.minute + df.index.second) % 900 == 0
    assert not inpace.sum() < 1  # make sure we remove less than 20 values
    df = df[inpace]

    # convert lon/lat to UTM 19 meters
    trans = pyproj.Transformer.from_crs("+proj=lonlat", "+proj=utm +zone=19")
    x, y = trans.transform(df.lon, df.lat)
    df["x"] = x  # points[:, 0]
    df["y"] = y  # points[:, 1]

    # resample with 15 minute frequency and fill with NaN
    df = df.resample("15min").mean()

    # compute derivative using savgol filter
    def derive(x):
        return scipy.signal.savgol_filter(
            x, window_length=20, polyorder=2, delta=1, deriv=1
        )
    df["fvx"] = derive(df.x) * 60 * 24 * 365 / 15.0
    df["fvy"] = derive(df.y) * 60 * 24 * 365 / 15.0
    df["fvz"] = derive(df.z) * 60 * 24 * 365 / 15.0

    # compute cartesian velocity in meters per year
    pos = df[["x", "y", "z"]]
    vel = (pos.diff(1) - pos.diff(-1)) / 2.0
    # vel2 = (pos.diff(2)-pos.diff(-2))/2.0
    # vel = vel1*4/3 + vel2/6
    # # vel = (-pos[4:]+8*pos[3:-1]-8*pos[1:-3]+pos[:-4])/12
    vel *= 60 * 24 * 365 / 15.0
    vel.columns = ["vx", "vy", "vz"]
    df = df.join(vel)

    # compute velocity polar coordinates
    df["vh"] = (df["vx"] ** 2 + df["vy"] ** 2) ** 0.5
    df["fvh"] = (df["fvx"] ** 2 + df["fvy"] ** 2) ** 0.5
    df["azimuth"] = np.arctan2(df["vy"], df["vx"] ** 2) * 180 / np.pi  # FIXME
    df["altitude"] = np.arctan2(df["vz"], df["vh"]) * 180 / np.pi

    # return the whole dataframe
    return df


def read_gnss_strain(lower=1, upper=3):
    """Compute longitudinal strain from raw data of two stations."""

    ldf = read_gnss_velocities(borehole=lower)
    udf = read_gnss_velocities(borehole=upper)
    distance = ((ldf.x - udf.x) ** 2 + (ldf.y - udf.y) ** 2) ** 0.5
    strain = (distance.diff(1) - distance.diff(-1)) / 2.0
    return strain


def read_gnss_strain_rate(lower=1, upper=2):
    """Compute longitudinal strain rate from raw data of two stations."""

    ldf = read_gnss_velocities(borehole=lower)
    udf = read_gnss_velocities(borehole=upper)
    distance = ((ldf.x - udf.x) ** 2 + (ldf.y - udf.y) ** 2) ** 0.5
    strain_rate = (ldf.fvh - udf.fvh) / distance
    return strain_rate


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=2, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 12.5, 'bottom': 12.5, 'top': 2.5,
            'hspace': 12.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # plot borehole velocity
    df = read_gnss_velocities(borehole=2)
    df.fvh.plot(ax=axes[0])
    df.vh.plot(ax=axes[0], alpha=0.5)

    # same thing from postprocessed data
    # pdf = bowtem_utils.load('../data/processed/bowdoin.bh1.gps.csv')
    # pdf.vh.plot(ax=axes[0], alpha=0.5)

    # read strain rate
    # strain = read_gnss_strain_rate()
    # strain.plot(ax=axes[1])

    # highpass-filter stress series
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(filt=None, resample='10min', tide=True)

    # apply transformation for plotting
    pres += 5 * (np.arange(len(pres.columns)))[::-1]
    tide = pres.pop('tide')

    # plot stress and tide data
    for ax in [axes[1]]:
        pres.plot(ax=ax, legend=False)
        tide.plot(ax=ax, c='C9')

        # set axes properties
        ax.grid(which='minor')
        ax.set_xlabel('')
        ax.set_ylabel('stress (kPa)')

        # add labels
        kwargs = {'fontsize': 6, 'fontweight': 'bold', 'transform': ax.transAxes}
        ax.text(1.01, 0, 'Pituffik\ntide' + r'$\,/\,$10', color='C9', **kwargs)
        for i, unit in enumerate(pres):
            ax.text(
                1.01, 0.9-0.1 * i, f"{unit}\n{depth[unit]:.0f}" r"$\,$m",
                color=f"C{i}", **kwargs)

    # set axes limits
    axes[0].grid(which='minor')
    # axes[1].set_ylim(-2.5, 47.5)
    # axes[1].set_xlim('20150707', '20150721')
    # axes[1].set_xlim('20160613', '20160721')
    # axes[1].set_xlim('20160707', '20160721')
    axes[0].set_ylim(0, 1000)

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
