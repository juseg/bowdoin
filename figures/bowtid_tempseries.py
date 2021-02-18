#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides temperature time series."""

from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import pandas as pd
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    fig, (ax0, ax1) = apl.subplots_mm(
        figsize=(180, 90), ncols=2, sharey=True, gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=2.5))

    # extract freezing dates
    # FIXME add util to load freezing dates
    temp = util.tid.load_inc('temp')['20140717':].resample('1H').mean()
    date = abs(temp-0.1*temp.max()-0.9*temp.min()).idxmin()

    # plot temperature data
    for ax in (ax0, ax1):
        temp.plot(ax=ax, legend=False, x_compat=True)
        ax.plot(date, [temp.loc[date[k], k] for k in temp], 'k+')

    # set axes properties
    ax0.set_ylabel('temperature (°C)')
    ax0.legend(ncol=3)

    # set up zoom
    ax1.set_xlim(*pd.to_datetime(['20140715', '20140915']))
    mark_inset(ax0, ax1, loc1=2, loc2=3, ec='0.5', ls='--')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
