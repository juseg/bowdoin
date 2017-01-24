# Figures Makefile

EXT = pdf
PY_FIGS = campaign_2016 \
          fft_gpsv fft_temp fft_tilt fft_wlev \
          hist_ls8 hist_ls8_uv \
          map_bow_dem map_bow_ls8 map_bow_ls8_uv map_bow_pal map_bow_s2a \
          map_bow_vgd map_bow_vgd_uv map_grl_gmb map_grl_vel \
          pf_temp pf_tilt spec_2015 summary \
          summer_2014 summer_2015 summer_2016 \
          ts_combined ts_drainage ts_gpsv ts_satvel ts_satvel_uv \
          ts_temp ts_tilt ts_wlev ts_tilt_dvel ts_tilt_avel ts_tilt_detrend

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
