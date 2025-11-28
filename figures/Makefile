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
BOWSTR_FILTERS = 12hbp 12hhp 24hbp 24hhp deriv
BOWSTR_FIGS = \
	$(addsuffix .png, \
		$(addprefix bowstr_, \
			boreholes fjordtide intervals \
			pgram specgrams timeseries wavelets) \
		$(addprefix bowstr_ccorr_, 12hbp 12hhp 24hbp 24hhp deriv) \
		$(addprefix bowstr_lines_, 12hbp 12hhp 24hbp 24hhp deriv) \
		$(addprefix bowstr_mcorr_, 12hbp 12hhp 24hbp 24hhp deriv) \
		$(addprefix bowstr_pgram_, stlsp stfft tilsp tifft))

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

# custom filter pattern rules
define GEN_FILTER_RULE
%_$(filter).png: %.py
	python $$< --filters $(filter)
endef
$(foreach filter,$(BOWSTR_FILTERS), \
  $(eval $(call GEN_FILTER_RULE)))

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
