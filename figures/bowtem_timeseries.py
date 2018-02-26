#!/usr/bin/env python2
# coding: utf-8

import util as ut
import pandas as pd


# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=1, ncols=1,
                            left=10.0, right=2.5, bottom=10.0, top=2.5)

# loop on boreholes
for bh, c in zip(ut.bowtem_bhnames, ut.bowtem_colours):

    # load data
    t, z, b = ut.io.load_bowtem_data(bh)

    # plot
    t.resample('1D').mean().plot(ax=ax, c=c, legend=False)

# set axes properties
ax.set_ylabel(u'temperature (°C)')
ax.set_ylim(-15.0, 1.0)

# save
ut.pl.savefig(fig)
