# Copyright (c) 2015-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Figures Makefile
# ================

# Targets
# -------

# bowdoin deformation figures (most outdated)
BOWDEF_FIGS = \
	$(addsuffix .png, \
		$(addprefix bowdef_, rates shear tilts))

# bowdoin stress figures
BOWSTR_FIGS = \
	$(addsuffix .png, \
		$(addprefix bowstr_, bores fjordtide intervals timeseries) \
		$(addprefix bowstr_ccorr_, 12hbp 12hhp 24hbp 24hhp deriv phase) \
		$(addprefix bowstr_lines_, 12hbp 12hhp 24hbp 24hhp deriv phase) \
		$(addprefix bowstr_mcorr_, 12hbp 12hhp 24hbp 24hhp deriv phase) \
		$(addprefix bowstr_pgram_, stlsp stfft tilsp tifft) \
		$(addprefix bowstr_sgram_, stcwt stfft ticwt tifft))

# bowdoin temperature figures
BOWTEM_FIGS = \
	$(addsuffix .png, \
		$(addprefix bowtem_, \
			boreholes calibration closure demseries images ogives profiles \
			timeseries))

# bowdoin paleo figures
BOWPAL_FIGS = \
	$(addsuffix .png, \
		$(addprefix bowpal_, samplemap))

# all bowdoin figures
ALL_FIGS = $(BOWDEF_FIGS) $(BOWTEM_FIGS) $(BOWSTR_FIGS) $(BOWPAL_FIGS)


# Rules
# -----

# default rule
all: $(ALL_FIGS)

# dependencies
$(ALL_FIGS): bowtem_utils.py matplotlibrc
$(BOWSTR_FIGS): bowstr_utils.py

# default pattern rule
%.png: %.py
	python $<

# optioned pattern rule
OPT_RULE = %_$(2).png: %.py ; python $$< --$(1) $(2)
$(foreach filter, 12hbp 12hhp 24hbp 24hhp deriv phase, \
  $(eval $(call OPT_RULE,filters,$(filter))))
$(foreach method, stcwt stlsp stfft ticwt tilsp tifft, \
  $(eval $(call OPT_RULE,methods,$(method))))

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
