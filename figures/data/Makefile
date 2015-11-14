# Data Makefile

# borehole names and inclinometer variables
BOREHOLES = upstream downstream
VARIABLES = temp tilt wlev

# processed files
GPS_FILES = processed/bowdoin-gps-upstream.csv
INC_FILES = $(foreach VAR,$(VARIABLES), \
              $(foreach BH,$(BOREHOLES), \
                processed/bowdoin-inclino-$(VAR)-$(BH).csv))
TEM_FILES = $(foreach BH,$(BOREHOLES), \
              processed/bowdoin-temperature-$(BH).csv)
PRE_FILES = $(foreach BH,$(BOREHOLES), \
              processed/bowdoin-pressure-$(BH).csv)
ALL_FILES = $(GPS_FILES) $(INC_FILES) $(PRE_FILES) $(TEM_FILES)

all: $(ALL_FILES)


$(GPS_FILES): preprocess-gps.py
	mkdir -p processed
	python2 $<

$(INC_FILES): preprocess-inclino.py
	mkdir -p processed
	python2 $<

$(TEM_FILES): preprocess-temperature.py
	mkdir -p processed
	python2 $<

$(PRE_FILES): preprocess-pressure.py
	mkdir -p processed
	python2 $<

.PHONY: clean

clean:
	rm -f processed/*
