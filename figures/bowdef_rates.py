#!/usr/bin/env python
# Copyright (c) 2019-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation tilt rates."""

import absplots as apl

import bowdef_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 90), nrows=2, sharex=True, gridspec_kw={
            'left': 15, 'right': 2.5, 'bottom': 10, 'top': 2.5, 'hspace': 2.5,
            'height_ratios': (2, 1)})

    # plot tilt rate
    tilt = bowdef_utils.load_tilt_rates(method='savgol', window='12h')
    tilt.plot(ax=axes[0], xlabel='', ylabel=r'tilt rate ($°\,a^{-1}$)')

    # plot tilt azimuth
    azimuth = bowdef_utils.load_tilt_azimuth(method='savgol', window='12h')
    azimuth.plot(ax=axes[1], legend=False, xlabel='', ylabel='tilt azimuth (°)')

    # set axes properties
    axes[0].legend(loc='upper right', ncols=2)
    axes[0].set_xlim('20140701', '20170801')
    axes[0].set_ylim(-1, 21)
    axes[1].set_xlim('20140701', '20170801')
    axes[1].set_yticks([-180, 0, 180])

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
