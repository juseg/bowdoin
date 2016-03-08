# Figures Makefile

EXT = pdf
PY_FIGS = fft_gpsv fft_temp fft_tilt fft_wlev \
          map_bow map_grl pf_temp pf_tilt summary \
          ts_combined ts_gpsv ts_temp ts_tilt ts_wlev \
          ts_tilt_dvel ts_tilt_avel ts_tilt_detrend
PY_FIGS := $(addsuffix .$(EXT), $(PY_FIGS))

PY_ANIS = anim_bowdoin_tilt.mp4

ALL_FIGS = $(PY_FIGS)
ALL_ANIS = $(PY_ANIS)

figs: data $(ALL_FIGS)

anim: $(ALL_ANIS)

$(PY_FIGS): %.pdf : %.py util matplotlibrc
	python2 $<

$(PY_ANIS): %.mp4 : %.py util matplotlibrc
	python2 $<

.PHONY: data clean cleandata

data:
	cd data && $(MAKE)

clean: cleandata
	rm -f $(ALL_FIGS) $(ALL_ANIS)

cleandata:
	cd data && $(MAKE) clean
