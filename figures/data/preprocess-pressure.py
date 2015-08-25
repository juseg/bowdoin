#!/usr/bin/env python2

import csv
import datetime

# for each borehole
sensors = ['073303', '094419']
for bh in [1, 2]:
    sensor = sensors[bh-1]

    # input and output file names
    ifilename = 'original/pressure/drucksens%s_final_storage_1.dat' % sensor
    ofilename = 'processed/bowdoin-pressure-bh%d.txt' % bh

    # open input file
    with open(ifilename, 'r') as ifile:
        reader = csv.reader(ifile, delimiter=',')

        # open output file
        with open(ofilename, 'w') as ofile:
            writer = csv.writer(ofile, delimiter=',')
            writer.writerow(['date', 'pressure'])

            # preprocess each row
            for row in reader:
                datestring = '%04d.%03d.%04d' % tuple(map(int, row[1:4]))
                date = datetime.datetime.strptime(datestring, '%Y.%j.%H%M')
                pressure = float(row[6])
                writer.writerow([date, pressure])
