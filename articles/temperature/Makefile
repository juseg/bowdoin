PAPER = bowdoin-temperature

all: $(PAPER).pdf

$(PAPER).pdf: $(PAPER).tex figures
	latexmk -pdf -dvi- -ps- $<

.PHONY: figures
figures:
	cd ../figures && $(MAKE)

.PHONY: clean
clean:
	latexmk -CA
