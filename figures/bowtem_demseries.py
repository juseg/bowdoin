#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature Arctic DEM time series."""

from scipy import stats
import xarray as xr
import cartopy.crs as ccrs
import absplots as apl
import util.tem


def main():
    """Main program called during execution."""

    # Arctic DEM strips with large data gaps
    # 'SETSM_W1W1_20150427_102001003C04A300_102001003ECD7100_seg1_2m_v3.0',
    # 'SETSM_W2W2_20150530_10300100421BB000_103001004254F700_seg1_2m_v3.0',
    # 'SETSM_W2W2_20150530_10300100421BB000_103001004254F700_seg2_2m_v3.0',
    # 'SETSM_W2W2_20150530_10300100421BB000_103001004254F700_seg3_2m_v3.0',
    # 'SETSM_WV02_20120512_103001001932B700_1030010018CB9600_seg6_2m_v3.0',

    # Arctic DEM strip with noisy-looking data
    # 'SETSM_W1W2_20150425_102001003DA28D00_10300100419E5700_seg4_2m_v3.0',

    # Arctic DEM strip used in published paper but gone missing from server
    # 'SETSM_W1W2_20140905_10200100318E9F00_1030010037BBC200_seg3_2m_v3.0',

    # Arctic DEM strips with small data gaps
    datastrips = [
        'SETSM_WV01_20120730_102001001C3CA200_102001001C997D00_seg2_2m_v3.0',
        'SETSM_WV02_20130404_1030010020AC5E00_1030010021347000_seg1_2m_v3.0',
        'SETSM_WV01_20140906_10200100318E9F00_1020010033454500_seg4_2m_v3.0',
        'SETSM_WV02_20140906_103001003766BC00_1030010036B2F000_seg1_2m_v3.0',
        'SETSM_WV02_20150419_10300100403C2300_1030010041149700_seg1_2m_v3.0',
        'SETSM_WV02_20160424_10300100566BCD00_103001005682C900_seg6_2m_v3.0',
        'SETSM_WV02_20160504_10300100557E8400_1030010055147100_seg1_2m_v3.0',
        'SETSM_WV01_20170318_10200100602AB700_102001005FDC9000_seg1_2m_v3.0']

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(180, 90), nrows=2, ncols=4, sharex=True, sharey=True,
        gridspec_kw=dict(
            left=2.5, right=17.5, wspace=2.5, bottom=2.5, top=5, hspace=5),
        subplot_kw=dict(projection=ccrs.Stereographic(
            central_latitude=90, central_longitude=-45,
            true_scale_latitude=70)))
    cax0, cax1 = fig.subplots_mm(nrows=2, gridspec_kw=dict(
        left=165, right=12.5, bottom=2.5, top=5, hspace=5))

    # loop on data strips
    for i, strip in enumerate(datastrips):
        ax = grid.flat[i]
        ax.set_rasterization_zorder(2.5)
        ax.set_title(strip[11:19])

        # load elevation data
        elev = xr.open_rasterio('../data/external/%s.tif' % strip)[0]
        elev = elev.loc[-1224000:-1229000, -537500:-532500].where(elev > -9999)

        # plot reference elevation map
        if i == 0:
            im0 = elev.plot.imshow(ax=ax, add_colorbar=False, add_labels=False,
                                   cmap='PuOr_r', vmin=0, vmax=200)
            ref = elev

        # plot normalized elevation using mode as zero
        else:
            diff = elev - ref
            diff = diff - stats.mode(diff, axis=None)[0]
            im1 = diff.plot.imshow(ax=ax, add_colorbar=False, add_labels=False,
                                   cmap='RdBu', vmin=-30, vmax=30)

    # add colorbar
    cbar = fig.colorbar(im0, cax=cax0, extend='both')
    cbar.set_label('surface elevation (m)')
    cbar = fig.colorbar(im1, cax=cax1, extend='both')
    cbar.set_label('elevation change (m)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
