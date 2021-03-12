# Article Makefile
# ================


# Variables
# ---------

PAPER = bowdoin-stress
REV = $(shell git describe --abbrev=0 --match=bowtid*)


# Rules
# -----

# default rule
pdf: $(PAPER).pdf

# default diff
diff: $(PAPER)-diff.pdf

# latex pdf patterned rule
%.pdf: %.tex ../../references/references.bib
	latexmk -pdf -dvi- -ps- $<

# latex diff patterned rule
%-diff.tex: %.tex
	latexdiff-vc --exclude-textcmd="section,subsection" --force --git -r $(REV) $<
	mv $(basename $@)$(REV).tex $@

# clean up
.PHONY: clean
clean:
	latexmk -pdf -CA
