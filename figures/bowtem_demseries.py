#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature Arctic DEM time series."""

from scipy import stats
import xarray as xr
import absplots as apl


def main():
    """Main program called during execution."""

    # Arctic DEM strips with large data gaps and coverage
    datastrips = [
        'WV02_20140906_103001003766BC00_1030010036B2F000_2m_lsf_seg1',  # 0.00
        'W1W2_20150425_102001003DA28D00_10300100419E5700_2m_lsf_seg1',  # 0.00
        'W1W1_20210916_10200100B7150300_10200100B787C400_2m_seg4',      # 0.08
        'W1W2_20150530_102001004109EA00_10300100421BB000_2m_lsf_seg3',  # 0.09
        'W2W2_20150530_10300100421BB000_1030010044C12100_2m_lsf_seg4',  # 0.12
        'W2W2_20150605_103001004254F700_1030010044C12100_2m_lsf_seg3',  # 0.15
        'W2W2_20150605_103001004254F700_1030010044C12100_2m_lsf_seg4',  # 0.20
        'W2W2_20150530_10300100421BB000_1030010044C12100_2m_lsf_seg5',  # 0.21
        'W2W2_20150530_10300100421BB000_1030010043544700_2m_lsf_seg3',  # 0.23
        'W1W2_20150530_102001004109EA00_10300100421BB000_2m_lsf_seg4',  # 0.25
        'W1W1_20210604_10200100B19AEB00_10200100B2C85700_2m_lsf_seg2',  # 0.30
        'WV03_20220411_104001007648AF00_1040010077B1F800_2m_lsf_seg1',  # 0.36
        'W1W1_20190725_102001008861F300_102001008C8B8C00_2m_lsf_seg4',  # 0.37
        'W1W1_20210907_10200100B7150300_10200100B7341500_2m_lsf_seg3',  # 0.42
        'W1W1_20210915_10200100B6373E00_10200100B7150300_2m_lsf_seg3',  # 0.42
        'W1W1_20210916_10200100B6DF1C00_10200100B7150300_2m_lsf_seg3',  # 0.44
        'W1W2_20150607_102001004109EA00_103001004254F700_2m_lsf_seg1']  # 0.45

    # Arctic DEM strips that look nothing like Bowdoin Glacier
    datastrips = [
        'W2W2_20150530_10300100421BB000_1030010043544700_2m_lsf_seg4',  # 0.72
        'W1W2_20150605_102001003F71CE00_1030010043544700_2m_lsf_seg2',  # 0.89
        'W2W2_20150605_103001004254F700_1030010043544700_2m_lsf_seg2',  # 0.87
        'WV01_20160501_102001004D1F3A00_102001004D362B00_2m_lsf_seg1']  # 0.94

    # Arctic DEM strips where mode subtraction fail to noisy data
    datastrips = [
        'W1W2_20150530_102001003F71CE00_10300100421BB000_2m_lsf_seg2',  # 0.96
        'W2W2_20150530_10300100421BB000_103001004254F700_2m_lsf_seg1',  # 1.00
        'W1W2_20150607_102001003F71CE00_103001004254F700_2m_lsf_seg2',  # 0.96
        'W1W1_20200620_102001009AD88700_102001009BE10900_2m_seg2',      # 0.56
        'W1W1_20210907_10200100B6DF1C00_10200100B7341500_2m_lsf_seg3']  # 0.92

    # Arctic DEM strips with unrealistically high sea level
    datastrips = [
        'W1W1_20150427_102001003C04A300_102001003ECD7100_2m_lsf_seg1',  # 0.90
        'W1W1_20190725_102001008861F300_102001008BA17900_2m_lsf_seg3',  # 0.90
        'W1W2_20190806_102001008BA17900_10300100971B7800_2m_seg2',      # 0.92
        'W1W1_20210607_10200100B2A1AD00_10200100B2C85700_2m_lsf_seg2',  # 0.99
        'W1W1_20210907_10200100B6373E00_10200100B7341500_2m_lsf_seg2',  # 1.00
        'W1W1_20210915_10200100B6373E00_10200100B6DF1C00_2m_lsf_seg3',  # 0.93
        'W1W1_20210915_10200100B6373E00_10200100B787C400_2m_seg1']      # 1.00

    # Arctic DEM strips with local terrain artifacts
    datastrips = [
        'WV02_20120512_103001001932B700_1030010018CB9600_2m_lsf_seg2',  # 0.91
        'WV02_20130401_1030010021317600_10300100214FD000_2m_seg3',      # 1.00
        'WV02_20190430_1030010093383A00_103001008F311A00_2m_lsf_seg1',  # 1.00
        'WV02_20210908_10300100C5296800_10300100C567F700_2m_seg2']      # 0.95

    # Arctic DEM strips with good coverage and quality
    datastrips = [
        'WV01_20120730_102001001C3CA200_102001001C997D00_2m_lsf_seg2',  # 0.83
        'WV02_20130404_1030010020AC5E00_1030010021347000_2m_lsf_seg1',  # 1.00
        'WV01_20140906_10200100318E9F00_1020010033454500_2m_lsf_seg2',  # 0.71
        'WV02_20140906_103001003766BC00_1030010036B2F000_2m_lsf_seg2',  # 0.81
        'WV02_20150419_10300100403C2300_1030010041149700_2m_lsf_seg1',  # 1.00
        'WV02_20160424_10300100566BCD00_103001005682C900_2m_lsf_seg1',  # 0.95
        'WV02_20160504_10300100557E8400_1030010055147100_2m_lsf_seg1',  # 0.75
        'WV01_20170318_10200100602AB700_102001005FDC9000_2m_lsf_seg1',  # 1.00
        'WV03_20180424_104001003C59FD00_104001003C25E800_2m_lsf_seg1',  # 0.90
        'WV01_20180502_10200100747CC100_10200100765FE000_2m_lsf_seg1',  # 1.00
        'WV02_20200318_10300100A3C33B00_10300100A5617100_2m_lsf_seg1',  # 0.76
        'WV02_20200410_10300100A31A0600_10300100A36D6500_2m_lsf_seg1',  # 0.89
        'W1W1_20200606_10200100965E3000_102001009A43F300_2m_lsf_seg5',  # 0.75
        'WV03_20201002_1040010060C03000_1040010061634200_2m_lsf_seg1',  # 0.96
        'WV02_20210501_10300100BD76C300_10300100BE22CD00_2m_lsf_seg1',  # 1.00
        'W1W1_20210922_10200100B6DF1C00_10200100B787C400_2m_seg2',      # 0.92
        'WV01_20220418_10200100C1DA0E00_10200100C4A08100_2m_lsf_seg1',  # 0.96
        'WV01_20230626_10200100DAA77300_10200100DBCCB300_2m_seg1',      # 1.00
        'WV01_20240701_10200100F18B1E00_10200100F1AFEA00_2m_seg1',      # 0.90
        'WV03_20240706_10400100989EFC00_1040010098D1C000_2m_seg1']      # 0.62

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(180, 90+130), nrows=2+3, ncols=4, sharex=True, sharey=True,
        gridspec_kw={
            'left': 2.5, 'right': 17.5, 'wspace': 2.5, 'bottom': 2.5, 'top': 5,
            'hspace': 5})
    cax0, cax1 = fig.subplots_mm(nrows=2, gridspec_kw={
        'left': 165, 'right': 12.5, 'bottom': 2.5, 'top': 5, 'hspace': 5})
    cax0.grid(False)  # see discussion of mpl issue #21723
    cax1.grid(False)  # see discussion of mpl issue #21723

    # loop on data strips
    for i, strip in enumerate(datastrips):
        ax = grid.flat[i]

        # load elevation data
        elev = xr.open_dataarray(f'../data/external/SETSM_s2s041_{strip}.tif')
        elev = elev.squeeze()
        elev = elev.where(elev > -9999)

        # plot reference elevation map
        if i == 0:
            im0 = elev.plot.imshow(ax=ax, add_colorbar=False, add_labels=False,
                                   cmap='PuOr_r', vmin=0, vmax=200)
            ref = elev

        # plot normalized elevation using mode as zero
        else:
            diff = elev - ref
            diff = diff - stats.mode(diff, axis=None, nan_policy='omit')[0]
            im1 = diff.plot.imshow(ax=ax, add_colorbar=False, add_labels=False,
                                   cmap='RdBu', vmin=-60, vmax=60)

        # set axes properties
        ax.set_rasterization_zorder(2.5)
        ax.set_title(strip[5:13])
        ax.set_xlim(-537500, -532500)
        ax.set_ylim(-1229000, -1224000)
        ax.set_xticks([])
        ax.set_yticks([])

    # add colorbar
    cbar = fig.colorbar(im0, cax=cax0, extend='both')
    cbar.set_label('surface elevation (m)')
    cbar = fig.colorbar(im1, cax=cax1, extend='both')
    cbar.set_label('elevation change (m)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()
