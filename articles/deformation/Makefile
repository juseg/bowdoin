# Article Makefile
# ================


# Variables
# ---------

PAPER = bowdoin-deformation


# Rules
# -----

# default rule
$(PAPER).pdf: $(PAPER).tex ../../references/references.bib
	latexmk -pdf -dvi- -ps- $<

# clean up
.PHONY: clean
clean:
	latexmk -pdf -CA
