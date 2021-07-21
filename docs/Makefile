# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =   # "-W" This flag turns warnings into errors.
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = Helios
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

clean:
	rm -rf "$(SOURCEDIR)/api"
	rm -rf "$(SOURCEDIR)/reference"
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) clean

html-examples:
	rm -rf "$(SOURCEDIR)/auto_examples"
	rm -rf "$(SOURCEDIR)/auto_tutorials"
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@echo $@
	$(SPHINXBUILD) -D plot_gallery=0 -b html $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)/html"
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)."
