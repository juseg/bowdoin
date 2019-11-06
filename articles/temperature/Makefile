# Article Makefile
# ================


# Variables
# ---------

PAPER = bowdoin-temperature
REV = $(shell git describe --abbrev=0 --match=bowtem*)


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


# Patterned rules
# ---------------

# stripped bib patterned rule
%.bib: %.aux ../../references/references.bib
	bibtool ../../references/references.bib -x $< > $@

# latex pdf patterned rule
%.pdf: %.tex ../../references/references.bib
	latexmk -pdf -dvi- -ps- $<

# latex rtf patterned rule (no eqs, no fields)
%.rtf: %.tex ../../references/references.bib
	latex2rtf -E0 -f0 $<

# libreoffice txt patterned rule (preserve special characters)
%.txt: %.rtf
	libreoffice --convert-to "txt:Text (encoded):UTF8" $<
	sed -i -n '/^Abstract/,/^References/p' $@

# latex diff patterned rule
%-diff.tex: %.tex
	latexdiff-vc --math-markup=3 --exclude-textcmd=section,subsection --force --git -r $(REV) $<
	mv $(basename $@)$(REV).tex $@

# clean up
.PHONY: clean
clean:
	latexmk -pdf -CA
