# Data Makefile

BOREHOLES = 1 2
FILES := $(foreach bh,$(BOREHOLES),processed/bowdoin-pressure-bh$(bh).txt)

all: $(FILES)

$(foreach bh,$(BOREHOLES),processed/bowdoin-%-bh$(bh).txt): preprocess-%.py
	python2 $<

.PHONY: clean

clean:
	rm -f processed/*
