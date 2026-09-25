#!/usr/bin/env python
# Copyright (c) 2016-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin velocity gradient from Landsat images."""


import absplots as apl
import xarray as xr

import bowtem_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 90), ncols=3, sharex=True, sharey=True, gridspec_kw={
            'left': 2.5, 'bottom': 2.5, 'right': 2.5, 'top': 2.5, 'wspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=fig.axes[0], color='w')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[1], color='k')
    bowtem_utils.add_subfig_label('(c)', ax=fig.axes[2], color='k')

    # plot image data
    bowtem_utils.plot_bowdoin_map(
        fig.axes[0], boreholes=['bh1', 'bh3'],
        colors=['tab:blue', 'tab:pink'], season='summer')

    # plot velocity contours
    prefix = '../data/satellite/bowdoin-landsat-uv/16072015_17082015_161111_1117'
    u = xr.open_dataarray(prefix+'_f_u.nc').squeeze().where(lambda x: x!=65535)
    v = xr.open_dataarray(prefix+'_f_v.nc').squeeze().where(lambda x: x!=65535)

    # compute rotated strain rates
    du_dx = u.differentiate('x')
    du_dy = u.differentiate('y')
    dv_dx = v.differentiate('x')
    dv_dy = v.differentiate('y')
    epp = (u**2*du_dx+u*v*(du_dy+dv_dx)+v**2*dv_dy) / (u**2+v**2)
    eoo = (v**2*du_dx-u*v*(du_dy+dv_dx)+ u**2*dv_dy) / (u**2+v**2)
    epo = (u*v*(dv_dy-du_dx)+0.5*(u**2-v**2)*(du_dy+dv_dx)) / (u**2+v**2)

    # long_strain.plot.contour(ax=ax, add_labels=False, alpha=0.75)
    # tran_strain.plot.contour(ax=ax, add_labels=False, alpha=0.75)
    # shear_strain.plot.contour(ax=ax, add_labels=False, alpha=0.75)

    # plot
    epp.plot.imshow(ax=axes[0], add_colorbar=False, add_labels=False, alpha=0.75)
    eoo.plot.imshow(ax=axes[1], add_colorbar=False, add_labels=False, alpha=0.75)
    epo.plot.imshow(ax=axes[2], add_colorbar=False, add_labels=False, alpha=0.75)

    # set axes properties
    # for ax in axes:
    #     ax.set_aspect('equal', adjustable='datalim')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
