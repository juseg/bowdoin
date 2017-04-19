#!/usr/bin/env python2


def cal_temperature(temp, depth, borehole):
    """
    Recalibrate downstream temperature to zero degrees.
    Unfortunately initial upstream data were lost.
    """

    # check argument validity
    assert borehole in ('downstream', 'upstream')

    # re-calibrate downstream borehole data to zero degrees
    if borehole == 'downstream':
        depth['temp01'] = 243.849292443  # FIXME: move this to preproc
        melt = melting_point(depth.iloc[0])  # FIXME: find nearest date
        calt = temp['2014-07-23 11:20':'2014-07-23 15:00'].mean()
        temp += (melt - calt).fillna(0.0)

    # return as dataframe
    return temp


def melting_point(depth, g=9.80665, rhoi=910.0, beta=7.9e-8):
    """Compute pressure melting point from depth (Luethi et al., 2002)"""
    return -beta * rhoi * g * depth
