#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature time series."""

import pandas as pd
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    gridspec_kw = dict(left=10, right=2.5, bottom=10, top=2.5)
    fig, ax = apl.subplots_mm(figsize=(150, 75), gridspec_kw=gridspec_kw)

    # for each borehole
    for bh, color in util.tem.COLOURS.items():

        # plot daily means
        temp, _, _ = util.tem.load_all(bh)
        temp = temp.resample('1D').mean()
        temp.plot(ax=ax, c=color, legend=False, lw=0.5)

        # add closure dates
        if bh != 'err':
            closure_dates = util.tem.estimate_closure_dates(bh, temp)
            closure_temps = [temp.loc[closure_dates[k], k] for k in temp]
            closure_temps = pd.Series(index=closure_dates, data=closure_temps)
            closure_temps.plot(ax=ax, color='k', marker='|', ls='')

    # add campaigns
    util.com.plot_field_campaigns(ax=ax)

    # set axes properties
    ax.set_ylabel(u'temperature (°C)')
    ax.set_xlim('20140615', '20170815')
    ax.set_ylim(-14.5, 0.5)

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
