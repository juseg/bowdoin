# Data Makefile

# borehole names and inclinometer variables
BOREHOLES = upstream downstream
INC_VARS = depth temp tilt wlev
TEM_VARS = depth temp
PRE_VARS = temp wlev

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

all: $(ALL_FILES)

$(GPS_FILES): preprocess-dgps.py
	mkdir -p processed
	python2 $<

$(INC_FILES): preprocess-tiltunit.py
	mkdir -p processed
	python2 $<

$(TEM_FILES): preprocess-thstring.py
	mkdir -p processed
	python2 $<

$(PRE_FILES): preprocess-pressure.py
	mkdir -p processed
	python2 $<

.PHONY: clean

clean:
	rm -f processed/*
