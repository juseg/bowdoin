# Figures Makefile
# ================


# Variables
# ---------

# all python figures
PY_CODE = $(addprefix bowtem_, arcticdem boreholes closure demseries \
                               profiles timeseries) \
          $(addprefix bowpal_, samplemap)
PY_FIGS = $(addsuffix .pdf, $(PY_CODE))

# all figures
ALL_FIGS = $(PY_FIGS)

# temporarily deactivated
# (tmp off: campaign_2016 summary \
#          $(addprefix bowdef_, profiles spectrogram \
#            $(addprefix fft_, gpsv tilt) \
#            $(addprefix hist_, ls8 ls8_uv) \
#            $(addprefix map_, dem gmb gsv ls8 ls8_uv vgd vgd_uv) \
#            $(addprefix summer_, 2014 2015 2016) \
#            $(addprefix ts_, angvel defvel detrended gpsvel satvel satvel_uv tilt)) \
#          $(addprefix bowtid_, boreholes correlate diffseries fft gmb \
#                               highpass intervals lombscargle previous \
#                               specgrams tempseries tideseries wlevseries) \
#          $(addprefix bowwat_, thinning wlevseries)


# Rules
# -----

# default rule
all: $(ALL_FIGS)

# make python figures
$(PY_FIGS): %.pdf : %.py matplotlibrc util
	python $<

# lint python code
lint:
	pylint -j 0 $(PY_CODE) util/???.py

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
