#!/usr/bin/env python2

import util as ut
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import gdal


def open_gtif(filename, extent):
    """Extract GeoTiff data over map extent and build coordinate vectors."""
    from osgeo.gdal import Open

    # open dataset
    dataset = Open(filename)
    #cols = dataset.RasterXSize
    #rows = dataset.RasterYSize

    # read geotransform params
    x0, dx, dxdy, y0, dydx, dy = dataset.GetGeoTransform()
    assert dxdy == dydx == 0.0  # rotation parameters should be zero

    # compute image indexes corresponding to map extent        
    w, e, s, n = extent
    wcol = int((w-x0)/dx)  # index of first (W) column
    nrow = int((n-y0)/dy)  # index of first (N) row
    ecol = int((e-x0)/dx) + 1  # index of last (E) column
    srow = int((s-y0)/dy) + 1  # index of last (S) row
    cols = ecol - wcol  # number of cols needed
    rows = srow - nrow  # number of rows needed

    # prepare coordinate vectors
    xwcol = x0 + (wcol+0.5)*dx  # x-coord of W row cell centers
    xecol = x0 + (ecol+0.5)*dx  # x-coord of E row cell centers
    ynrow = y0 + (nrow+0.5)*dy  # y-coord of N row cell centers
    ysrow = y0 + (srow+0.5)*dy  # y-coord of S row cell centers
    x = xwcol + np.arange(cols)*dx  # from W to E
    y = ysrow - np.arange(rows)*dy  # from S to N

    # equivalent using linspace
    #x = np.linspace(xwcol, xecol, cols)
    #y = np.linspace(ysrow, ynrow, rows)

    # read and flip elevation data
    sign = lambda f: 2*(f > 0) - 1
    z = dataset.ReadAsArray(wcol, nrow, cols, rows)
    z = z[::sign(dy), ::sign(dx)]

    # close dataset and return x, y, z
    dataset = None
    return x, y, z


def shading(x, y, z, azimuth=315.0, altitude=30.0):
    """Compute shaded relief map."""

    # convert to rad from the x-axis
    azimuth = (90.0-azimuth)*np.pi / 180.
    altitude = altitude*np.pi / 180.

    # compute cartesian coords of the illumination direction
    xlight = np.cos(azimuth) * np.cos(altitude)
    ylight = np.sin(azimuth) * np.cos(altitude)
    zlight = np.sin(altitude)
    #zlight = 0.0  # remove shades from horizontal surfaces

    # compute hillshade (dot product of normal and light direction vectors)
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    u, v = np.gradient(z, dx, dy)
    return (zlight - u*xlight - v*ylight) / (1 + u**2 + v**2)**(0.5)


def slope(x, y, z, smoothing=None):
    """Compute slope map with optional smoothing."""

    # optionally smooth data
    if smoothing:
        import scipy.ndimage as ndimage
        z = ndimage.filters.gaussian_filter(z, smoothing)

    # compute gradient along each coordinate
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    u, v = np.gradient(z, dx, dy)

    # compute slope
    slope = (u**2 + v**2)**0.5
    return slope


def imextent(x, y):
    """Compute image extent from coordinate vectors."""
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2
    return w, e, s, n


if __name__ == '__main__':

    # projections and map boundaries
    ll = ccrs.PlateCarree()
    proj = ccrs.Stereographic(central_latitude=90.0, central_longitude=-45.0,
                              true_scale_latitude=70.0)

    # subregion w, e, s, n
    #extents = (-540e3, -525e3, -1230e3, -1215e3)  # lower Bowdoin Glacier
    extents = (-540e3, -531e3, -1231e3, -1225e3)  # boreholes

    # read velocity data
    filename = ('data/external/gimpdem0_4.tif')
    x, y, z = open_gtif(filename, extents)

    # initialize figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection=proj)

    # set rasterization levels
    ax.set_rasterization_zorder(2.5)

    # set map extents
    #ax.set_extent(grld, crs=proj)

    # plot shadows
    ax.imshow(shading(x, y, z), extent=imextent(x, y),
              cmap='Greys', vmin=0.0, vmax=1.0)

    # plot contours
    levs = np.arange(0.0, 1500.0, 20.0)
    cs = ax.contour(x, y, z, levels=levs[(levs % 100 != 0)],
                    colors='k', linewidths=0.1)
    cs = ax.contour(x, y, z, levels=levs[(levs % 100 == 0)],
                    colors='k', linewidths=0.25)
    cs.clabel(fmt='%d')

    # plot slope map
    #s = slope(x, y, z, smoothing=10)
    #im = ax.imshow(s, extent=imextent(x, y), vmin=0.0, vmax=0.05, cmap='magma_r')
    #fig.colorbar(im)

    # plot locations of camera and boreholes
    llz = {'qaanaaq':   (-69.230556, 77.466667,   0.000000),
           'cam_lower': (-68.527481, 77.659782, 490.219243),
           'cam_upper': (-68.504852, 77.691702, 289.044237),
           'gcp_m1':    (-68.504733, 77.688107, 139.879200),
           'gcp_m2':    (-68.628121, 77.721004, 172.288962),
           'gcp_m3':    (-68.643724, 77.703824, 172.562631),
           'bh1':       (-68.555749, 77.691244,  88.694913),  # upstream
           'bh2':       (-68.555685, 77.691307,  87.746263),  # upstream
           'bh3':       (-68.558857, 77.689995,  83.446628),  # downstream
           'camp':      (-68.509920, 77.685890,  70.000000)}
    ax.plot(*llz['bh1'][:2], c=ut.colors[1], marker='o', ms=6,  transform=ll)
    ax.plot(*llz['bh3'][:2], c=ut.colors[0], marker='o', ms=6, transform=ll)
    ax.plot(*llz['cam_upper'][:2], c=ut.palette[7], marker='^', ms=6, transform=ll)
    ax.plot(*llz['cam_lower'][:2], c=ut.palette[7], marker='^', ms=6, transform=ll)

    # save third frame
    fig.savefig('map_bow')

