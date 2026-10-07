#!/usr/bin/env python
# Copyright (c) 2019-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation tilt azimuth."""

import absplots as apl

import bowdef_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
        'left': 15, 'right': 2.5, 'bottom': 10, 'top': 2.5})

    # plot tilt azimuth
    azimuth = bowdef_utils.load_tilt_azimuth(method='kernel', window='3h')
    azimuth.plot(ax=ax, xlabel='', ylabel='tilt azimuth (°)')

    # set axes properties
    ax.legend(loc='upper right', ncols=2)
    ax.set_xlim('20140701', '20170801')
    ax.set_yticks([-180, 0, 180])

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
