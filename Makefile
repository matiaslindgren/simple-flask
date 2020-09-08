OUTDIR=/mnt/c/tmp

.PHONY: readme

readme:
	cat README.md | python3 -c 'import sys, mistune; print(mistune.html(sys.stdin.read()))' > $(OUTDIR)/readme.html
