#!/usr/bin/env python

import numpy as np
import cartopy.crs as ccrs
import absplots as apl
import util as ut

# Arctic DEM strips with large data gaps
    #'SETSM_W1W1_20150427_102001003C04A300_102001003ECD7100_seg1_2m_v3.0',
    #'SETSM_W2W2_20150530_10300100421BB000_103001004254F700_seg1_2m_v3.0',
    #'SETSM_W2W2_20150530_10300100421BB000_103001004254F700_seg2_2m_v3.0',
    #'SETSM_W2W2_20150530_10300100421BB000_103001004254F700_seg3_2m_v3.0',
    #'SETSM_WV02_20120512_103001001932B700_1030010018CB9600_seg6_2m_v3.0',
    #'SETSM_WV02_20150419_10300100403C2300_1030010041149700_seg1_2m_v3.0',

# Arctic DEM strips with small data gaps
datastrips = [
    'SETSM_WV01_20120730_102001001C3CA200_102001001C997D00_seg2_2m_v3.0',
    'SETSM_WV02_20130404_1030010020AC5E00_1030010021347000_seg1_2m_v3.0',
    'SETSM_W1W2_20140905_10200100318E9F00_1030010037BBC200_seg3_2m_v3.0',
    'SETSM_WV01_20140906_10200100318E9F00_1020010033454500_seg4_2m_v3.0',
    'SETSM_WV02_20140906_103001003766BC00_1030010036B2F000_seg1_2m_v3.0',
    'SETSM_W1W2_20150425_102001003DA28D00_10300100419E5700_seg4_2m_v3.0',
    'SETSM_WV02_20160424_10300100566BCD00_103001005682C900_seg6_2m_v3.0',
    'SETSM_WV02_20160504_10300100557E8400_1030010055147100_seg1_2m_v3.0',
    'SETSM_WV01_20170318_10200100602AB700_102001005FDC9000_seg1_2m_v3.0']

# initialize figure
proj = ccrs.Stereographic(central_latitude=90.0, central_longitude=-45.0,
                          true_scale_latitude=70.0)
fig, grid = apl.subplots_mm(figsize=(150, 145), nrows=3, ncols=3,
                            sharex=True, sharey=True, projection=proj,
                            gridspec_kw=dict(left=2.5, right=15, wspace=2.5,
                                             bottom=2.5, top=5, hspace=5))
cax0, cax1 = fig.subplots_mm(ncols=1, nrows=2,
                             gridspec_kw=dict(left=137.5, right=10,
                                              bottom=2.5, top=5, hspace=52.5))

# loop on data strips
for i, strip in enumerate(datastrips):
    ax = grid.flat[i]
    ax.set_extent([-537.5e3, -532.5e3, -1229e3, -1224e3], crs=ax.projection)
    ax.set_rasterization_zorder(2.5)
    ax.set_title(strip[11:19])

    # load elevation data
    # FIXME try rasterio / salem
    elev, extent = ut.io.open_gtif('../data/external/%s.tif' % strip)
    elev = np.ma.masked_equal(elev, -9999.0)

    # plot reference elevation map
    if i == 0:
        im0 = ax.imshow(elev, extent=extent, vmin=0, vmax=200, cmap='PuOr_r')
        ref = elev

    # plot normalized elevation change
    else:
        diff = elev - ref
        diff = diff - diff[4500:, 2250:3750].mean()  # FIXME use an ice mask
        im1 = ax.imshow(diff, extent=extent, vmin=-30, vmax=30, cmap='RdBu')

# add colorbar
cb = fig.colorbar(im0, cax=cax0, extend='both')
cb.set_label('surface elevation (m)')
cb = fig.colorbar(im1, cax=cax1, extend='both')
cb.set_label('elevation change (m)')

# save figure
ut.pl.savefig(fig)