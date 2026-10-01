# Data Makefile
# =============


# Variables
# ---------

# satellite data from Daiki
SAT_FILES = satellite/bowdoin-landsat.csv satellite/bowdoin-landsat-uv


# Rules
# -----

# default rule
all: external processed $(SAT_FILES)

# retrieve external files
external: retrieve-external.sh
	bash $<

# preprocess borehole data
processed: preprocess-boreholes.py
	python $<

# process landsat data from Daiki
# FIXME: use similar paradigm as for other projects
satellite/bowdoin-%.csv: preprocess-%.py
	python $<

# extract landsat velocity components from Daiki
satellite/bowdoin-landsat-uv: satellite/bowdoin-landsat-uv.zip
	unzip -nq -d satellite $<
	touch $@

# clean up
# FIXME: use similar paradigm as for other projects
.PHONY: clean
clean:
	rm -rf external processed satellite/bowdoin-landsat $(SAT_FILES)
