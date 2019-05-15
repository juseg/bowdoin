#!/usr/bin/env python

import numpy as np
import pandas as pd
import absplots as apl
import util as ut


# initialize figure
fig, ax = apl.subplots_mm(figsize=(150, 75),
                          gridspec_kw=dict(left=10, right=2.5,
                                           bottom=10, top=2.5))

# loop on boreholes
for bh, c in zip(ut.bowtem_bhnames, ut.bowtem_colours):

    # load data
    t, z, b = ut.io.load_bowtem_data(bh)
    t = t['2014-07':].resample('1D').mean()

    # extract days to freezing
    d0 = pd.to_datetime(ut.bowtem_bhdates[int(bh[-1])-1])  # drilling dates
    d1 = t['2014-07'].notnull().idxmax()  # start of record
    df = t[d0+pd.to_timedelta('1D'):].diff().idxmin()  # date of freezing
    df[df == t.index[1]] = np.nan

    # plot
    t.resample('1D').mean().plot(ax=ax, c=c, legend=False, x_compat=True)
    ax.plot(df, [t.loc[df[k], k] for k in t], 'k+')

# set axes properties
ax.set_ylabel(u'temperature (°C)')
ax.set_ylim(-15.0, 1.0)

# save
ut.pl.savefig(fig)
