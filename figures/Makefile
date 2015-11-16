# Figures Makefile

PY_FIGS = temperature-profile.pdf timeseries.pdf
ALL_FIGS = $(PY_FIGS)

all: data $(ALL_FIGS)

$(PY_FIGS): %.pdf : %.py matplotlibrc projectglobals.py
	python2 $<

.PHONY: data clean cleandata

data:
	cd data && $(MAKE)

clean: cleandata
	rm -f $(ALL_FIGS)

cleandata:
	cd data && $(MAKE) clean
