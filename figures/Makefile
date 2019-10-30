# Figures Makefile
# ================


# Variables
# ---------

# python code
DEF_CODE = $(addprefix bowdef_, strainrates)
TEM_CODE = $(addprefix bowtem_, boreholes calibration closure demseries \
	                        images ogives profiles timeseries)
TID_CODE = $(addprefix bowtid_, diffseries fjordtide highpass intervals
                                tempseries timeseries)
PAL_CODE = $(addprefix bowpal_, samplemap)
ALL_CODE = $(DEF_CODE) $(TEM_CODE) $(TID_CODE) $(PAL_CODE)

# python figures
DEF_FIGS = $(addsuffix .pdf, $(DEF_CODE))
TEM_FIGS = $(addsuffix .pdf, $(TEM_CODE))
TID_FIGS = $(addsuffix .pdf, $(TID_CODE))
PAL_FIGS = $(addsuffix .pdf, $(PAL_CODE))
ALL_FIGS = $(addsuffix .pdf, $(ALL_CODE))

# temporarily deactivated
# (tmp off: campaign_2016 summary \
#          $(addprefix bowdef_, profiles spectrogram \
#            $(addprefix fft_, gpsv tilt) \
#            $(addprefix hist_, ls8 ls8_uv) \
#            $(addprefix map_, gmb gsv ls8 ls8_uv vgd vgd_uv) \
#            $(addprefix summer_, 2014 2015 2016) \
#            $(addprefix ts_, defvel detrended gpsvel satvel satvel_uv tilt)) \
#          $(addprefix bowtid_, boreholes correlate fft gmb \
#                               highpass intervals lombscargle previous \
#                               specgrams) \
#          $(addprefix bowwat_, thinning wlevseries)


# Rules
# -----

# default rule
all: $(ALL_FIGS)

# project dependencies
$(DEF_FIGS): util/inc.py
$(TEM_FIGS): util/tem.py
$(TID_FIGS): util/tid.py

# make python figures
$(ALL_FIGS): %.pdf : %.py matplotlibrc util/com.py util/geo.py
	LC_ALL=en_US.utf8 python $<

# lint python code
lint:
	pylint -j 0 $(ALL_CODE) util/???.py

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
