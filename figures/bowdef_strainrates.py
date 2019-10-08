#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin strain rate time series."""

import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw=dict(
        left=17.5, right=2.5, bottom=12.5, top=2.5))

    # plot each borehole
    for bh in ('bh1', 'bh3'):

        # load strain rate
        exz = util.inc.load_strain_rate(bh)

        # plot strain rate
        exz.plot(ax=ax)

    # set axes properties
    ax.legend(ncol=2)
    ax.set_ylabel(r'strain rate ($m\,a^{-1}$')
    ax.set_xlim('20140615', '20170815')
    ax.set_ylim(0, 0.35)

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
