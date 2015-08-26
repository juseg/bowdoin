#!/usr/bin/env python2

import csv
import datetime

# parameters
borehole = 2  # 1 (lower) or 2 (upper)
sensor = 6  # assuming this corresponds to the pressure sensor

# for each borehole
for bh in [1, 2]:

    # input and output file names
    ifilename = 'original/inclino/BOWDOIN-%i_All.dat' % bh
    ofilename = 'processed/bowdoin-inclino-bh%d.txt' % bh

    # open input file
    with open(ifilename, 'rU') as ifile:
        reader = csv.reader(ifile, delimiter=',')

        # read headers
        header = [s.strip('"') for s in reader.next()]
        labels = [s.strip('"') for s in reader.next()]
        dummy = reader.next()
        dummy = reader.next()

        # expected line pattern
        nsites = len(labels) - 4

        # open output file
        with open(ofilename, 'w') as ofile:
            writer = csv.writer(ofile, delimiter=',')
            writer.writerow(['date'] + ['site%02d' % i for i in range(1, nsites+1)])

            # preprocess each row
            for i, row in enumerate(reader):
                datestring = row[0]
                date = datetime.datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')
                values = []
                for j in range(nsites):
                    sitestring = row[j+4]
                    try:
                        values.append(float(sitestring.split(',')[sensor]))
                    except IndexError, ValueError:
                        values.append(9999.0)
                writer.writerow([date] + values)
