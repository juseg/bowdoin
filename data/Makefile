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
processed: preprocess-boreholes.py
	python2 $<

# process landsat data from Daiki
# FIXME: use similar paradigm as for other projects
satellite/bowdoin-%.csv: preprocess-%.py
	python2 $<

# clean up
# FIXME: use similar paradigm as for other projects
.PHONY: clean
clean:
	rm -rf external processed satellite/bowdoin-landsat satellite/bowdoin-landsat-uv $(SAT_FILES)
