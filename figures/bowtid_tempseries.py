#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import util
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import absplots as apl


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(figsize=(180, 90), ncols=2, sharey=True,
        gridspec_kw=dict(
            left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=2.5))

    # extract freezing dates
    t = ut.io.load_bowtid_data('temp')['20140717':].resample('1H').mean()
    df = abs(t-0.1*t.max()-0.9*t.min()).idxmin()  # date of freezing

    # plot temperature data
    for ax in grid:
        t.plot(ax=ax, legend=False, x_compat=True)
        ax.plot(df, [t.loc[df[k], k] for k in t], 'k+')

    # set axes properties
    grid[0].set_ylabel('temperature (°C)')
    grid[0].legend(ncol=3)

    # set up zoom
    x0, x1 = '20140715', '20140915'
    grid[1].set_xlim(x0, x1)
    mark_inset(grid[0], grid[1], loc1=2, loc2=3, ec='0.5', ls='--')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()
