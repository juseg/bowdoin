#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin strain rate time series."""

import absplots as apl
import bowtem_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
        'left': 17.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5})

    # plot each borehole
    for bh in ('bh1', 'bh3'):

        # load strain rate
        exz = bowtem_utils.load_strain_rate(bh)*60*60*24*365.25

        # plot strain rate
        exz.plot(ax=ax)

    # set axes properties
    ax.legend(ncol=2)
    ax.set_ylabel(r'strain rate ($a^{-1}$)')
    ax.set_xlim('20140615', '20170815')
    ax.set_ylim(0, 0.35)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
