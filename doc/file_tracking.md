File tracking
=============

In many cases, PGF figures will be used to plot external data. If you are using
a build system, it is useful to have this automatically rebuild the figure when
the data is changed. To this end, pgfutils can be told to monitor any files
that are opened and output them at the end of the compilation. This is enabled
by setting the `PGFUTILS_TRACK_FILES` environment variable. If this variable is
set to 1 (or no value is given), then the list of files is output to `stdout`.
If it is set to 2, the list is printed to `stderr`. Any other value is
interpreted as a filename, and the list written to that file.

The tracked files are output in the format `mode:filename`, where mode is `r`
for files that were read (dependencies) and `w` for files that were written
(generated files). Only files in or below the current directory will be
included in the list. Note that the read files will include the `pgfutils.cfg`
file if it exists, and that the written files will *not* include the final PGF
figure (typically, the only written files that are reported are any rasterised
images that are included in the figure).

Internally, this feature works by wrapping some standard Python file opening
functions (such as `open()`) and keeping a list of any relevant filenames.
There are some caveats to the tracking:

* Any code which uses low-level file handling (e.g., a compiled extension which
  directly calls C file handling functions, or code which uses the low-level
  functions in the `os` module) will bypass this tracking.
* Any code which uses file descriptors (e.g., with `os.fdopen`) will bypass the
  tracking.
* Any uses of the standard file opening functions *before* you have called
  `setup_figure()` will not be noticed.
* Any code which stores an internal reference to a standard file opening
  function *before* you have called `setup_figure()` will bypass the tracking.

The most likely example of this final point is NumPy: its data-loading module
stores an internal reference to `io.open`. If you import NumPy (or anything
which uses it, such as Matplotlib) before calling `setup_figure()` then some
NumPy file operations will not be noticed. This seems to mainly affect CSV or
other text files; `.npy` files are opened through a separate mechanism which
appears to still get tracked. Nonetheless, it is recommended you import and
call `setup_figure` at the very start of your script.
