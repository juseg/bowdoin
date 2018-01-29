# Data Makefile
# =============


# Variables
# ---------

# satellite data from Daiki
SAT_FILES = satellite/bowdoin-landsat.csv satellite/bowdoin-landsat-uv.csv


# Rules
# -----

# default rule
all: external processed $(SAT_FILES)

# retrieve external files
external: retrieve-external.sh
	bash $<

# gps data is a special case
# FIXME: merge these two scripts
processed: preprocess-boreholes.py preprocess-dgps.py
	mkdir -p processed
	python2 preprocess-boreholes.py
	python2 preprocess-dgps.py

# process landsat data from Daiki
# FIXME: use similar paradigm as for other projects
satellite/bowdoin-%.csv: preprocess-%.py
	python2 $<

# clean up
.PHONY: clean
clean:
	rm -rf external processed $(SAT_FILES)
