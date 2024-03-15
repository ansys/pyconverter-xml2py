# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -j auto
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
# TODO: these lines of code until $(SPHINXBUILD) should be removed once the feature branch is merged
	pip freeze > temp_req.txt;
	@if grep -q "sphinx-autoapi @ git+https://github.com/ansys/sphinx-autoapi" temp_req.txt;\
		then\
			echo found;\
		else\
			pip uninstall --yes sphinx-autoapi;\
			pip install "sphinx-autoapi @ git+https://github.com/ansys/sphinx-autoapi@feat/single-page-stable";\
	fi
	rm temp_req.txt;\
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O);

clean:
	rm -rf $(BUILDDIR)/*

pdf:
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
	(test -f $(BUILDDIR)/latex/pyconverter-xml2py-Documentation-*.pdf && echo pdf exists) || exit 1
