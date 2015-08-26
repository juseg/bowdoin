# Figures Makefile

PY_FIGS = plot-inclino.pdf plot-pressure.pdf plot-temperature.pdf
ALL_FIGS = $(PY_FIGS)

all: data $(ALL_FIGS)

$(PY_FIGS): %.pdf : %.py matplotlibrc
	python2 $<

.PHONY: data clean cleandata

data:
	cd data && $(MAKE)

clean: cleandata
	rm -f $(ALL_FIGS)

cleandata:
	cd data && $(MAKE) clean
