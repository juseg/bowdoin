# Figures Makefile

PY_FIGS = pf_temp.pdf \
    ts_combined.pdf ts_gpsv.pdf ts_temp.pdf ts_tilt.pdf ts_wlev.pdf \

ALL_FIGS = $(PY_FIGS)

all: data $(ALL_FIGS)

$(PY_FIGS): %.pdf : %.py util matplotlibrc
	python2 $<

.PHONY: data clean cleandata

data:
	cd data && $(MAKE)

clean: cleandata
	rm -f $(ALL_FIGS)

cleandata:
	cd data && $(MAKE) clean
