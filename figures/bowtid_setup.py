#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

distances = {'U':2.0, 'L':1.85}

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(85.0, 60.0),
                            left=12.0, right=1.5, bottom=9.0, top=1.5)

# plot tilt unit depths
z = ut.io.load_depth('tiltunit', 'both')
for u in z.index:
    x = distances[u[0]]
    ax.plot(x, z[u], marker='s')
    ax.text(x+0.01, z[u], u[0::3], va='center')

# add base line
zp = ut.io.load_depth('pressure', 'both')
for u in zp.index:
    x = distances[u[0]]
    b = max(zp[u], z[z.index.str.startswith(u[0])].max())
    ax.plot([x, x], [b, 0.0], 'k-_')

# add flow direction arrow
ax.text(0.9, 0.55, 'ice flow', ha='center', transform=ax.transAxes)
ax.annotate('', xy=(0.85, 0.5), xytext=(0.95, 0.5),
            xycoords=ax.transAxes, textcoords=ax.transAxes,
            arrowprops=dict(arrowstyle='->',  lw=1.0))

# set axes properties
ax.set_xlim(1.75, 2.15)
ax.set_xticks(distances.values())
ax.set_xlabel('approximate distance from front in 2014 (km)')
ax.set_ylabel('depth (m)')
ax.invert_yaxis()

# save
ut.pl.savefig(fig)
