# Data Makefile

BOREHOLES = upstream downstream
VARIABLES = inclino pressure temperature
FILES := $(foreach VAR,$(VARIABLES), \
           $(foreach BH,$(BOREHOLES), \
             processed/bowdoin-$(VAR)-$(BH).csv))

all: $(FILES)

$(foreach bh,$(BOREHOLES),processed/bowdoin-%-$(bh).csv): preprocess-%.py
	mkdir -p processed
	python2 $<

.PHONY: clean

clean:
	rm -f processed/*
