#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

distances = [2.0, 1.85]

# initialize figure
fig, ax = plt.subplots(1, 1, sharey=True)  # FIXME: use iceplotlib subplots

# for each borehole
for i, bh in enumerate(ut.boreholes):
    x = distances[i]

    z = ut.io.load_data('tiltunit', 'depth', bh)
    # plot tilt unit locations
    for u in z:
        label = bh[0].upper() + u[-1]  # FIXME: move to preprocessing
        ax.plot(x, z[u], marker='s', label=label)
        ax.text(x+0.01, z[u], label, va='center')

    # add base line
    b = ut.io.load_depth('pressure', bh).squeeze()
    b = max(b, z.squeeze().max())
    ax.plot([x, x], [b, 0.0], 'k-_')

# add flow direction arrow
ax.text(0.9, 0.55, 'ice flow', ha='center', transform=ax.transAxes)
ax.annotate('', xy=(0.85, 0.5), xytext=(0.95, 0.5),
            xycoords=ax.transAxes, textcoords=ax.transAxes,
            arrowprops=dict(arrowstyle='->',  lw=1.0))

# set axes properties
ax.set_xlim(1.75, 2.15)
ax.set_xticks(distances)
ax.set_xlabel('approximate distance from front in 2014 (km)')
ax.set_ylabel('depth (m)')
ax.invert_yaxis()

# save
ut.pl.savefig(fig)
