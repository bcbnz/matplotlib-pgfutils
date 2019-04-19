default: twocol.pdf

twocol.pdf: twocol.tex single.pypgf double.pypgf
	xelatex twocol

%.pypgf: %.py pgfutils.cfg
	python $?

.PHONY: clean

clean:
	rm -f threecol.{aux,log,pdf}
	rm -f {single,double,triple}.pypgf
