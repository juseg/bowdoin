#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation against GNSS velocity."""

import absplots as apl
import numpy as np
import pandas as pd

import bowdef_utils
import bowstr_utils
import bowtem_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=4, sharex=True, gridspec_kw={
            'left': 12.5, 'right': 12.5, 'bottom': 12.5, 'top': 2.5,
            'height_ratios': (3, 3, 2, 1), 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # plot borehole velocity
    df = bowdef_utils.load_gnss_velocities(method='twopoint')
    df.vh.plot(ax=axes[0], color='0.9')
    df = bowdef_utils.load_gnss_velocities(method='savgol')
    df.vh.plot(ax=axes[0], color='tab:blue')

    # read strain rate
    # strain = read_gnss_strain_rate()
    # strain.plot(ax=axes[1])

    # highpass-filter stress series
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(filt=None, resample='10min', tide=True)
    tide = pres.pop('tide')
    pres = pres / 1e3

    # plot tilt rate (6h = 36*10min)
    tilx = bowstr_utils.load(variable='tilx').resample('10min').mean()
    tily = bowstr_utils.load(variable='tily').resample('10min').mean()
    tilx = tilx.interpolate(limit_area='inside', method='linear')
    tily = tily.interpolate(limit_area='inside', method='linear')
    kwargs = {'window_length': 72, 'polyorder': 2, 'delta': 1, 'deriv': 1}
    tilx = bowdef_utils.filter_savgol_dataframe(tilx, **kwargs)
    tily = bowdef_utils.filter_savgol_dataframe(tily, **kwargs)
    tilt = np.arccos(np.cos(tilx)*np.cos(tily)) * 180 / np.pi
    tilt = tilt[tilt.index >= '2014-07-17']
    tilt *= 3600 * 24 * 365.25 / pd.to_timedelta('10min').total_seconds()
    tilt.plot(ax=axes[1], legend=False)

    # plot stress and tide data
    pres.plot(ax=axes[2], legend=False)
    tide.plot(ax=axes[3], c='C9')

    # add labels
    for i, unit in enumerate(pres):
        axes[2].text(
            1.01, 1.6-0.2*i, f'{unit}\n{depth[unit]:.0f}' r'$\,$m',
            color=f'C{i}', fontsize=6, fontweight='bold',
            transform=axes[2].transAxes)
    axes[3].text(
        1.01, 0, 'Pituffik\ntide'+r'$\,/\,$10', color='C9',
        fontsize=6, fontweight='bold', transform=axes[3].transAxes)

    # set axes limits
    axes[0].grid(which='minor')
    axes[1].grid(which='minor')
    axes[2].grid(which='minor')
    axes[3].set_xlabel('')
    axes[0].set_ylabel(r'velocity ($m\,a^{-1}$)', labelpad=0)
    axes[1].set_ylabel(r'tilt rate ($°\,a^{-1}$)')
    axes[2].set_ylabel('stress (MPa)')
    axes[3].set_ylabel('tide (kPa)', labelpad=0)
    axes[0].set_ylim(-50, 950)
    axes[1].set_ylim(-1, 21)
    axes[2].set_ylim(-0.15, 3.15)
    axes[3].set_ylim(-2.4, 2.4)

    # zoom on tidal oscillations
    # axes[0].set_xlim('20160801', '20161001')
    # axes[1].set_ylim(-1, 14)
    # axes[2].set_ylim(1.99, 2.14)

    # save
    fig.savefig(__file__[:-3])


if __name__ == "__main__":
    main()
