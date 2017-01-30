# Figures Makefile
# ================


# Variables
# ---------

# default figure extension
EXT = pdf

# python executable
PY = python2

# all python figures
PY_FIGS = campaign_2016 \
          $(addprefix fft_, gpsv temp tilt wlev) \
          $(addprefix hist_, ls8 ls8_uv) \
          $(addprefix map_, \
            $(addprefix bow_, dem ls8 ls8_uv pal s2a vgd vgd_uv) \
            $(addprefix grl_, gmb vel)) \
          $(addprefix pf_, temp tilt) \
          spec_2015 summary \
          $(addprefix summer_, 2014 2015 2016) \
          $(addprefix ts_, combined drainage gpsv satvel satvel_uv temp \
                           tilt tilt_dvel tilt_avel tilt_detrend wlev)
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
	rm $(ALL_FIGS)
