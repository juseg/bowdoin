# Figures Makefile
# ================


# Variables
# ---------

# python code
DEF_CODE = $(addprefix bowdef_, )
TEM_CODE = $(addprefix bowtem_, boreholes calibration closure demseries \
	                        images ogives profiles timeseries)
STR_CODE = $(addprefix bowstr_, \
    boreholes correlate diffseries freezedates fourier fjordtide highpass \
    intervals lombscargle rollcorr specgrams timeseries wavelets)
PAL_CODE = $(addprefix bowpal_, samplemap)
ALL_CODE = $(DEF_CODE) $(TEM_CODE) $(STR_CODE) $(PAL_CODE)

# python figures
DEF_FIGS = $(addsuffix .pdf, $(DEF_CODE))
TEM_FIGS = $(addsuffix .pdf, $(TEM_CODE))
STR_FIGS = $(addsuffix .pdf, $(STR_CODE))
PAL_FIGS = $(addsuffix .pdf, $(PAL_CODE))
ALL_FIGS = $(addsuffix .pdf, $(ALL_CODE))

# temporarily deactivated
# (tmp off: campaign_2016 summary \
#          $(addprefix bowdef_, profiles spectrogram strainrate \
#            $(addprefix fft_, gpsv tilt) \
#            $(addprefix hist_, ls8 ls8_uv) \
#            $(addprefix map_, gsv ls8 ls8_uv vgd vgd_uv) \
#            $(addprefix summer_, 2014 2015 2016) \
#            $(addprefix ts_, defvel detrended gpsvel satvel satvel_uv tilt)) \
#          $(addprefix bowwat_, thinning wlevseries)


# Rules
# -----

# default rule
all: $(ALL_FIGS)

# project dependencies
$(DEF_FIGS): util/inc.py
$(TEM_FIGS): util/tem.py
$(STR_FIGS): util/str.py

# make python figures (alt use LC_ALL=en_GB.utf8 python)
$(ALL_FIGS): %.pdf : %.py matplotlibrc util/com.py util/geo.py
	python $<

# lint python code
lint:
	pylint -j 0 $(ALL_CODE) util/???.py

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
