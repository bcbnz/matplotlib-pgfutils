default: twocol.pdf

twocol.pdf: twocol.tex single.pypgf double.pypgf
	xelatex twocol

%.pypgf: %.py pgfutils.cfg
	python $?
