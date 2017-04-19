#!/usr/bin/env python2


def cal_temperature(temp, borehole):
    """
    Recalibrate downstream temperature to zero degrees.
    Unfortunately initial upstream data were lost.
    """

    # check argument validity
    assert borehole in ('downstream', 'upstream')

    # re-calibrate downstream borehole data to zero degrees
    if borehole == 'downstream':
        temp -= temp['2014-07-23 11:20':'2014-07-23 15:00'].mean()

    # return as dataframe
    return temp
