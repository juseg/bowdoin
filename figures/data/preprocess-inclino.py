#!/usr/bin/env python2

import csv
import datetime
import numpy as np

# input and output instrument names
input_instruments = ['id', 'ax', 'ay', 'mx', 'my', 'mz', 'p', 'tp', 't']
output_instruments = ['ax', 'ay', 'p', 't']

# for each borehole
for bh in [1, 2]:
    print 'Processing data for borehole %d...' % bh

    # input and output file names
    cfilename = 'original/inclino/BOWDOIN-%i_Coefs.dat' % bh
    ifilename = 'original/inclino/BOWDOIN-%i_All.dat' % bh
    ofilename = 'processed/bowdoin-inclino-bh%d.txt' % bh

    # read calibration coefficients
    coeffs = np.loadtxt(cfilename)

    # open input file
    with open(ifilename, 'rU') as ifile:
        reader = csv.reader(ifile, delimiter=',')

        # read headers
        header = [s.strip('"') for s in reader.next()]
        labels = [s.strip('"') for s in reader.next()]
        dummy = reader.next()
        dummy = reader.next()

        # number of sensor units
        nsites = len(labels) - 4

        # open output file
        with open(ofilename, 'w') as ofile:
            writer = csv.writer(ofile, delimiter=',')

            # write header line
            names = ['date'] + ['%s%02d' % (inst, site)
                                for site in range(nsites)
                                for inst in output_instruments]
            writer.writerow(names)

            # for each row
            for i, row in enumerate(reader):

                # read date tag
                datestring = row[0]
                date = datetime.datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')

                # initialize lists of values
                values = []

                # for each site on the sensor chain
                for j, sitestring in enumerate(row[4:]):
                    sitevalues = sitestring.split(',')

                    # fill empty data with null values
                    if sitestring == '':
                        values += [np.nan]*4

                    # ignore otherwise incomplete records
                    elif (len(sitevalues) != 9):
                        print ('Ignore incomplete unit record on row %d: "%s"'
                               % (i+5, sitestring))
                        values += [np.nan]*4

                    # else try to read values
                    else:

                        # try to read tilt values
                        try:
                            ax = float(sitevalues[1])
                            ay = float(sitevalues[2])
                            cx = coeffs[2*j]
                            cy = coeffs[2*j+1]
                            ax = (ax - cx[1])/cx[0]
                            ay = (ay - cy[1])/cy[0]
                        except ValueError:
                            ax = ay = np.nan

                        # try to read pressure values
                        try:
                            p = float(sitevalues[6])
                        except ValueError:
                            p = np.nan

                        # try to read temperature values
                        try:
                            t = float(sitevalues[8])
                        except ValueError:
                            t = np.nan

                        # append all values
                        values += [ax, ay, p, t]

                # write data
                writer.writerow([date] + values)
