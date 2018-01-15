#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(85.0, 65.0),
                            left=12.0, right=1.5, bottom=9.0, top=1.5)

# plot tilt unit water level
p = ut.io.load_bowtid_data('temp').resample('1D').mean()
p.plot(ax=ax)

# add label
ax.set_ylabel(u'temperature (°C)')
ax.legend(ncol=3)

# save
ut.pl.savefig(fig)
