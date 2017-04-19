# Data Makefile
# =============


# Variables
# ---------

# borehole names and processed variables
BOREHOLES = upstream downstream
INC_VARS = depth temp tiltx tilty wlev
TEM_VARS = depth temp
PRE_VARS = depth temp wlev

# processed borehole data
GPS_FILES = processed/bowdoin-dgps-velocity-upstream.csv
INC_FILES = $(foreach VAR, $(INC_VARS), \
              $(foreach BH, $(BOREHOLES), \
                processed/bowdoin-tiltunit-$(VAR)-$(BH).csv))
TEM_FILES = $(foreach VAR, $(TEM_VARS), \
              $(foreach BH, $(BOREHOLES), \
                processed/bowdoin-thstring-$(VAR)-$(BH).csv))
PRE_FILES = $(foreach VAR, $(PRE_VARS), \
              $(foreach BH, $(BOREHOLES), \
                processed/bowdoin-pressure-$(VAR)-$(BH).csv))

# satellite data from Daiki
SAT_FILES = satellite/bowdoin-landsat.csv \
            satellite/bowdoin-landsat-uv.csv

# all files to process
ALL_FILES = $(GPS_FILES) $(INC_FILES) $(PRE_FILES) $(TEM_FILES) $(SAT_FILES)


# Rules
# -----

# default rule
all: external $(ALL_FILES)

# retrieve external files
external: retrieve-external.sh
	bash $<

# gps data is a special case
$(GPS_FILES): preprocess-dgps.py
	mkdir -p processed
	python2 $<

# additional dependency of tilt processing on pressure water levels
preprocess-tiltunit.py: $(foreach BH, $(BOREHOLES), \
                          processed/bowdoin-pressure-wlev-$(BH).csv)

# general patterned rule to avoid multiple calls
$(foreach VAR, $(INC_VARS), \
  $(foreach BH, $(BOREHOLES), \
    processed/bowdoin-%-$(VAR)-$(BH).csv)): preprocess-%.py util.py
	mkdir -p processed
	python2 $<

# process landsat data from Daiki
satellite/bowdoin-%.csv: preprocess-%.py
	python2 $<

# clean up
.PHONY: clean
clean:
	rm -rf external processed $(SAT_FILES)
