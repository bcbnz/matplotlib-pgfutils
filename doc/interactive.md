Interactive mode
================

[IPython][1] includes an [interactive plotting mode][2] which supports
automatically showing Matplotlib figures. This can be started by using the
`--matplotlib` option when running IPython, or by issuing the magic command
`%matplotlib` in an IPython session.

To assist in debugging your scripts, when pgfutils detects it is running in
IPython with this interactive mode enabled, the `save()` call will display the
figure rather than saving it. From here you can further tweak the figure with
standard Matplotlib functions rather than having to edit the script and
recompile your TeX document. Note that this will not give an exact preview as
the size of the figure will not be the same as in the final document. The fonts
will almost certainly differ as well. However, it is useful for checking the
correct data is plotted, choosing limits, deciding on labels etc.

[1]: https://ipython.org/
[2]: https://ipython.readthedocs.io/en/stable/interactive/plotting.html
