# Data Makefile

# borehole names and inclinometer variables
BOREHOLES = upstream downstream
VARIABLES = temp tilt wlev

# processed files
GPS_FILES = processed/bowdoin-dgps-velocity-upstream.csv
INC_FILES = $(foreach VAR,$(VARIABLES), \
              $(foreach BH,$(BOREHOLES), \
                processed/bowdoin-tiltunit-$(VAR)-$(BH).csv))
TEM_FILES = $(foreach BH,$(BOREHOLES), \
              processed/bowdoin-thstring-temp-$(BH).csv)
PRE_FILES = $(foreach BH,$(BOREHOLES), \
              processed/bowdoin-pressure-wlev-$(BH).csv)
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
