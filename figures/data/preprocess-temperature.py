#!/usr/bin/env python2

import csv
import datetime
import numpy as np

# for each borehole
for bh in [1, 2]:

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
                date = datetime.datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')
                values = map(float, row[3:19])  # use resistances only
                writer.writerow([date] + values)
