#!/usr/bin/env python
# Copyright (c) 2019-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation tilt azimuths."""

# FIXME consider plotting azimuths alongside tilt rates

import absplots as apl

import bowdef_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
        'left': 15, 'right': 2.5, 'bottom': 10, 'top': 2.5})

    # plot tilt rate
    azimuth = bowdef_utils.load_tilt_azimuth(method='savgol', window='12h')
    azimuth.plot(ax=ax, xlabel='', ylabel=r'tilt rate ($°\,a^{-1}$)')
    # precession = filter_derive_dataframe(azimuth, method='twopoint')

    # set axes properties
    ax.legend(loc='upper right', ncols=3)
    ax.set_xlim('20140701', '20170801')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
