# Figures Makefile
# ================


# Variables
# ---------

# default figure extension
EXT = pdf

# python executable
PY = python2

# all python figures
PY_FIGS = campaign_2016 summary \
          $(addprefix bowdef_, profiles spectrogram \
            $(addprefix fft_, gpsv tilt) \
            $(addprefix hist_, ls8 ls8_uv) \
            $(addprefix map_, dem gmb gsv ls8 ls8_uv vgd vgd_uv) \
            $(addprefix summer_, 2014 2015 2016) \
            $(addprefix ts_, angvel defvel detrended gpsvel satvel satvel_uv tilt)) \
          $(addprefix bowpal_, samplemap) \
          $(addprefix bowtem_, boreholes closure profiles timeseries) \
          $(addprefix bowtid_, boreholes correlate diffseries fft gmb \
                               highpass intervals lombscargle previous \
                               specgrams tempseries tideseries wlevseries) \
          $(addprefix bowwat_, thinning wlevseries)
PY_FIGS := $(addsuffix .$(EXT), $(PY_FIGS))

# all figures
ALL_FIGS = $(PY_FIGS)



# Rules
# -----

# default rule
all: $(ALL_FIGS)

# rules and dependencies for python figures
$(PY_FIGS): %.pdf : %.py matplotlibrc util
	$(PY) $<

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
