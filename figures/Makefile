# Figures Makefile

EXT = pdf
PY_FIGS = fft_gpsv fft_temp fft_tilt fft_wlev \
          map_bow map_grl pf_temp pf_tilt \
          ts_combined ts_gpsv ts_temp ts_tilt ts_wlev \
          ts_tilt_dvel ts_tilt_avel ts_tilt_detrend
PY_FIGS := $(addsuffix .$(EXT), $(PY_FIGS))

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
