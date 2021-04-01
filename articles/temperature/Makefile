# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Article Makefile
# ================

# Variables
# ---------

PAPER = bowdoin-temperature
BIB = ../../../references/references.bib
REV = $(shell git describe --abbrev=0 --match=bowstr*)


# Named rules
# -----------

# default rule
pdf: $(PAPER).pdf

# stripped bib
bib : $(PAPER).bib

# richt text format
rtf: $(PAPER).rtf

# plain text format
txt: $(PAPER).txt

# default diff
diff: $(PAPER)-diff.pdf

# figures zip file
figs: $(PAPER)-figs.zip


# Patterned rules
# ---------------

#stripped bib patterned rule
%.bib: %.aux $(BIB)
	bibtool $(BIB) -d -q -x $< > $@

# latex pdf patterned rule
%.pdf: %.tex $(BIB)
	latexmk -pdf $<

# latex rtf patterned rule (no eqs, no fields)
%.rtf: %.tex $(BIB)
	latex2rtf -E0 -f0 $<

# libreoffice txt patterned rule (preserve special characters)
%.txt: %.rtf
	libreoffice --convert-to "txt:Text (encoded):UTF8" $<
	sed -i -n '/^Abstract/,/^References/p' $@

# latex diff patterned rule
%-diff.tex: %.tex
	latexdiff-vc --disable-citation-markup --force --git -r $(REV) $<
	mv $(basename $@)$(REV).tex $@

# figures zip patterned rule
# %-figs.zip: SHELL:=/bin/bash
%-figs.zip: %.tex
	i=01; \
	grep includegraphics $< | while read line; \
	do \
	   fig=$${line:27:-2}; \
	   cp -v ../../figures/$$fig.pdf fig$$i.pdf; \
	   sed -i "s/\includegraphics{$$fig}/\includegraphics{fig$$i}/" $<; \
	   i="$$(printf '%02d' $$((10#$$i+1)))"; \
	done; \
	zip $@ fig??.pdf; \
	rm fig??.pdf


# Clean up
# --------

.PHONY: clean
clean:
	latexmk -pdf -CA && rm $(PAPER).{bbl,bib,rtf,txt}
