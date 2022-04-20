.. Copyright (c) 2017--2020, Julien Seguinot (juseg.github.io)
.. Creative Commons Attribution-ShareAlike 4.0 International License
.. (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

Bowdoin Glacier borehole temperature data
-----------------------------------------

Files [required]::

   bowdoin.bh1.inc.dept.csv
   bowdoin.bh1.inc.temp.csv
   bowdoin.bh2.pzm.dept.csv
   bowdoin.bh2.pzm.temp.csv
   bowdoin.bh2.thr.dept.csv
   bowdoin.bh2.thr.temp.csv
   bowdoin.bh3.inc.dept.csv
   bowdoin.bh3.inc.temp.csv
   bowdoin.bh3.pzm.dept.csv
   bowdoin.bh3.pzm.temp.csv
   bowdoin.bh3.thr.dept.csv
   bowdoin.bh3.thr.temp.csv

Communities [recommended]
   --

Upload type [required]
   Dataset

Basic information [required]
   Digital Object Identifier
      10.5281/zenodo.3695961

   Publication date
      2020-03-03

   Title
      Bowdoin Glacier borehole temperature data

   Authors
      Seguinot, Julien
      Funk, Martin
      Bauder, Andreas
      Wyder, Thomas
      Senn, Cornelius
      Sugiyama, Shin

   Description
      These data contain temperature observation made between July 2014 and
      July 2017 in three boreholes drilled 2 km from the calving front of
      Bowdoin Glacier (Kangerluarsuup Sermia) in northwestern Greenland.

      **Reference**:

      * J. Seguinot, M. Funk, A. Bauder, T. Wyder, C. Senn and S. Sugiyama.
        Englacial warming indicates deep crevassing in Bowdoin Glacier, Greenland,
        *Frontiers in Earth Sciences*, 8:65,
        https://doi.org/10.3389/feart.2020.00065, 2020.

      **File names**::

         bowdoin.bh{1|2|3}.{inc|pzm|thr}.{dept|temp}.csv

      * Borehole locations:

        - *bh1*: drilled 2 km from the calving front

           - 2014-07-16: 77.6912 °N, 68.5557 °E, 89 m
           - 2016-07-19: 77.6855 °N, 68.5681 °E, 63 m
           - 2017-07-14: 77.6832 °N, 68.5748 °E, 58 m

        - *bh2*: drilled 7 m away from BH1

           - 2014-07-17: 77.6913 °N, 68.5557 °E, 88 m
           - 2016-07-19: 77.6856 °N, 68.5680 °E, 60 m
           - 2017-07-14: 77.6833 °N, 68.5748 °E, 57 m

        - *bh3*: drilled 158 m downstream of BH1

           - 2014-07-22: 77.6900 °N, 68.5589 °E, 83 m
           - 2016-07-19: 77.6843 °N, 68.5726 °E, 43 m
           - 2017-07-14: 77.6819 °N, 68.5800 °E, 54 m

      * Instrument types:

        - *inc*: digital inclinometers
        - *pzm*: basal piezometers
        - *thr*: thermistor strings

      * Variables:

        - *dept*: initial sensor depth according to remaining cable lenghts
        - *temp*: temperature times series after recalibration

      **Data format**:

      The data use comma-separated plain text format (csv). Negative depths
      imply that sensors are located on the glacier surface. Sensor depths
      higher than the borehole depths imply that cables are not fully
      stretched. The data can be read by e.g. Pandas using::

         pd.read_csv(filename, parse_dates=True, index_col='date')

      **Changelog:**

      * Version 1:

         - Initial version.

   Version
      --

   Language
      en

   Keywords
      greenland, glacier, ice, temperature

   Additional notes
      This work was supported by the Swiss National Science Foundation (SNSF)
      grants 200020-169558 and 200021-153179/1, and the Japanese Ministry of
      Education, Culture, Sports, Science of Technology through the GRENE
      Arctic Climate Change Research Project and Arctic Challenge for
      Sustainability (ArCS) project.

License [required]
   Open Access / Creative Commons Attribution 4.0

Funding [recommended]
   -- (not working)

Related/alternate identifiers [recommended]
   https://doi.org/10.3389/feart.2020.00065 is supplemented by this upload.

Contributors [optional]
   --

References [optional]
   --

Conference [optional]
   --

Book/Report/Chapter [optional]
   --

Thesis [optional]
   --

Subjects [optional]
   --

