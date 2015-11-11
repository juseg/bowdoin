# Data Makefile

BOREHOLES = upstream downstream
VARIABLES = inclino pressure temperature
FILES := processed/bowdoin-gps-upstream.csv \
         $(foreach VAR,$(VARIABLES), \
           $(foreach BH,$(BOREHOLES), \
             processed/bowdoin-$(VAR)-$(BH).csv))

all: $(FILES)

processed/bowdoin-gps-upstream.csv: preprocess-gps.py
	mkdir -p processed
	python2 $<

$(foreach BH,$(BOREHOLES),processed/bowdoin-inclino-$(BH).csv)): preprocess-inclino.py
	mkdir -p processed
	python2 $<

$(foreach BH,$(BOREHOLES),processed/bowdoin-temperature-$(BH).csv)): preprocess-temperature.py
	mkdir -p processed
	python2 $<

$(foreach BH,$(BOREHOLES),processed/bowdoin-pressure-$(BH).csv)): preprocess-pressure.py
	mkdir -p processed
	python2 $<

.PHONY: clean

clean:
	rm -f processed/*
