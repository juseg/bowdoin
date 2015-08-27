#!/usr/bin/env python2

import csv
import datetime
import numpy as np

# for each borehole
for bh in [1, 2]:

    # read rearranged calibration coefficients
    # borehole 1: BH2A[1-9] + BH2B[1-7]
    # borehole 2: BH1A[1-9] + BH1B[1-4,7,5-6]
    coefpath = 'original/temperature/Th-Bowdoin-%i_Coefs.dat' % bh
    coefs = np.loadtxt(coefpath)
    a1 = coefs[:,0]
    a2 = coefs[:,1]
    a3 = coefs[:,2]

    # input and output file names
    ifilename = 'original/temperature/Th-Bowdoin-%i_Therm.dat' % bh
    ofilename = 'processed/bowdoin-temperature-bh%d.txt' % bh

    # open input file
    with open(ifilename, 'r') as ifile:
        reader = csv.reader(ifile, delimiter=',')
        header = [s.strip('"') for s in reader.next()]
        labels = [s.strip('"') for s in reader.next()]
        dummy = reader.next()
        dummy = reader.next()

        # open output file
        with open(ofilename, 'w') as ofile:
            writer = csv.writer(ofile, delimiter=',')
            writer.writerow(['date'] + ['res%02d' % i for i in range(1, 17)])

            # preprocess each row
            for row in reader:
                datestring = row[0]
                date = datetime.datetime.strptime(datestring,
                                                  '%Y-%m-%d %H:%M:%S')
                res = np.array(map(float, row[3:19]))
                temp = 1 / (a1 + a2*np.log(res) + a3*(np.log(res))**3) - 273.15
                writer.writerow([date] + list(temp))
