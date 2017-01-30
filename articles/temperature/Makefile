# Article Makefile
# ================


# Variables
# ---------

PAPER = bowdoin-temperature


# Rules
# -----

# default rule
$(PAPER).pdf: $(PAPER).tex
	latexmk -pdf -dvi- -ps- $<

# clean up
.PHONY: clean
clean:
	latexmk -CA
