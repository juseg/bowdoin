#!/usr/bin/env python2

import matplotlib.pyplot as plt
import netCDF4 as nc4
import util as ut

if __name__ == '__main__':

    # initialize figure
    fig, ax = plt.subplots()

    # plot histogram
    basename = '16072015_17082015_161111_1117_f'
    upath = '../data/satellite/bowdoin-landsat-uv/%s_u.nc' % basename
    vpath = '../data/satellite/bowdoin-landsat-uv/%s_v.nc' % basename
    unc = nc4.Dataset(upath)
    vnc = nc4.Dataset(vpath)
    u = unc['z'][:]
    v = vnc['z'][:]
    unc.close()
    vnc.close()
    c = (u**2+v**2)**0.5
    ax.hist(c.compressed(), bins=range(0,451,1), ec='none', fc=ut.palette['darkorange'])

    # save
    fig.savefig('hist_ls8_uv')
