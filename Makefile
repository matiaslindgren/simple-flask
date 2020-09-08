OUTDIR=.

.PHONY: readme archive

readme:
	cat README.md | python3 -c 'import sys, mistune; print(mistune.html(sys.stdin.read()))' > $(OUTDIR)/readme.html

archive:
	git archive master --format=zip --prefix=message-app/ --output=$(OUTDIR)/message-app.zip
