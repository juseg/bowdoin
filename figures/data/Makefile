# Data Makefile

# borehole names and inclinometer variables
BOREHOLES = upstream downstream
INC_VARS = depth temp tiltx tilty wlev
TEM_VARS = depth temp
PRE_VARS = depth temp wlev

# processed files
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
ALL_FILES = $(GPS_FILES) $(INC_FILES) $(PRE_FILES) $(TEM_FILES)

# default rule
all: $(ALL_FILES) external satellite/bowdoin-landsat.csv

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
    processed/bowdoin-%-$(VAR)-$(BH).csv)): preprocess-%.py
	mkdir -p processed
	python2 $<

# retrieve external files
external: retrieve-external.sh
	bash $<

# process landsat data from Daiki
satellite/bowdoin-landsat.csv: preprocess-landsat.py
	python2 $<

# clean processed and downloaded files
.PHONY: clean
clean:
	rm -rf processed external
