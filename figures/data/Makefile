# Data Makefile

BOREHOLES = 1 2
VARIABLES = pressure temperature
FILES := $(foreach VAR,$(VARIABLES), \
           $(foreach BH,$(BOREHOLES), \
             processed/bowdoin-$(VAR)-bh$(BH).txt))

all: $(FILES)

$(foreach bh,$(BOREHOLES),processed/bowdoin-%-bh$(bh).txt): preprocess-%.py
	python2 $<

.PHONY: clean

clean:
	rm -f processed/*
