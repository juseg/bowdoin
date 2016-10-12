#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import cartopy.io.shapereader as shpreader
#import cartopy.feature as cfeature

### Functions ###

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

def imextent(x, y):
    """Compute image extent from coordinate vectors."""
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2
    return w, e, s, n

def annotated_scatter(ax, points, text, textpos):
    """Draw scatter plot with text labels."""
    ax.scatter(points[:,0], points[:,1], c='red')
    for i, xy in enumerate(points):
        isright = (textpos[i][1] == 'r')
        isup = (textpos[i][0] == 'u')
        xoffset = (2*isright - 1)*20
        yoffset = (2*isup - 1)*20
        ax.annotate(text[i], xy=xy, xytext=(xoffset, yoffset),
                    textcoords='offset points',
                    ha=('left' if isright else 'right'),
                    va=('bottom' if isup else 'top'),
                    bbox=dict(boxstyle='square,pad=0.5', fc='w'),
                    arrowprops=dict(arrowstyle='->', color='k',
                                    relpos=(1-isright, 1-isup)))

### Main program ###

if __name__ == "__main__":

    # projections and map boundaries
    ll = ccrs.PlateCarree()
    proj = ccrs.UTM(19)
    w, e, s, n = 509e3, 513e3, 8619e3, 8622e3  # just around the samples

    # extend map boundaries
    f = 1.0  # zoom-out factor
    w = (1+f)*w/2 + (1-f)*e/2
    e = (1+f)*e/2 + (1-f)*w/2
    s = (1+f)*s/2 + (1-f)*n/2
    n = (1+f)*n/2 + (1-f)*s/2

    # initialize figure
    figw, figh = 297.0, 210.0
    fig = plt.figure(figsize=(figw/25.4, figh/25.4))
    ax = fig.add_subplot('111', projection=proj)
    fig.subplots_adjust(left=10.0/figw, right=1-10.0/figw,
                        bottom=10.0/figh, top=1-10.0/figh)
    ax.set_extent([w, e, s, n], crs=proj)
    #ax.set_rasterization_zorder(2.5)

    # open Yvo's digital elevation model
    x, y, z = open_gtif('data/bowdoin_20100904_15m_20140929.tif', (w, e, s, n))

    # plot shadows
    ax.imshow(shading(x, y, z), extent=imextent(x, y),
              cmap='Greys', vmin=0.0, vmax=1.0)

    # plot contours
    levs = np.arange(0.0, 800.0, 10.0)
    cs = ax.contour(x, y, z, levels=levs[(levs % 100 != 0)],
                    colors='k', linewidths=0.25)
    cs = ax.contour(x, y, z, levels=levs[(levs % 100 == 0)],
                    colors='k', linewidths=0.5)
    cs.clabel(fmt='%d')

    # plot sample locations
    samples = np.genfromtxt('samples.txt', dtype=None, names=True)
    points = proj.transform_points(ll, samples['longitude'], samples['latitude'])[:,:2]
    text = ['%s\n%.0f m' % (s['name'], s['elevation']) for s in samples]
    textpos = ['ul', 'lr', 'ul', 'lr', 'ul', 'lr', 'lr', 'll', 'ul']
    annotated_scatter(ax, points, text, textpos)

    # plot camera location
    ax.plot(-68.527481, 77.659782, 'b^', transform=ll)

# save
plt.savefig('map_bartlett')
