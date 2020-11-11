File tracking
=============

In many cases, PGF figures will be used to plot external data. If you are using
a build system, it is useful to have it automatically rebuild the figure when
the data is changed. To this end, pgfutils can be told to monitor any files
that are opened and output them at the end of the compilation. This tracking
will also include any Python files which are imported. Only files in specific
directories are tracked -- the corresponding configuration options are detailed
below.

The tracking is enabled by setting the `PGFUTILS_TRACK_FILES` environment
variable. If this variable is set to 1 (or no value is given), then the list of
files is output to `stdout`.  If it is set to 2, the list is printed to
`stderr`. Any other value is interpreted as a filename, and the list written to
that file.

The tracked files are output in the format `mode:filename`, where mode is `r`
for files that were read (dependencies) and `w` for files that were written
(generated files). If the file is underneath the top-level project directory,
the filename will be relative. If it is outside the project directory, it will
be an absolute filename.  For an example of using this file tracking in a build
system, see the [latexmk integration](latexmk.md) documentation.


Data dependencies
-----------------

Any file which is opened for reading only is treated as a possible dependency.
Each of these files is checked to see if it is in one of the directories
specified in the `data` key of the `[paths]` section of [the
configuration](config.md), or in a sub-directory of one of those directories.
If so, it is counted as a dependency. Note that this will include the
`pgfutils.cfg` configuration file if it exists (assuming the top-level
directory has not been removed from the list of dependency paths).


Python imports
--------------

Any imported modules which are from directories (or their sub-directories) in
the `paths.pythonpath` and `paths.extra_import` configuration settings are
treated as dependencies. Note that by default this does not include any
libraries installed system-wide or in a user-specific location -- if you want
this, you can add the appropriate directories to the `paths.extra_import`
[configuration option](config.md).


Generated files
---------------

The generated files will *not* include the final PGF figure (typically, the
only written files that are reported are any rasterised images that are
included in the figure).


Automatic tracking
------------------

Most files read by a script can be automatically tracked by pgfutils.
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


Extra tracking
--------------

By default, tracking is only installed on standard Python functions. If you use
the [netCDF4][1] library, tracking can also be enabled for files opened by it
(which includes other libraries that use netCDF4, such as xarray). To enable
this project-wide, set the `extra_tracking` option to `netCDF4` in your
configuration:

```INI
[pgfutils]
extra_tracking = netCDF4
```

To only enable it for a specific figure, add the option to the ``setup_figure``
call:

```python
setup_figure(width=1, height=0.4, extra_tracking="netCDF4")
```


Manual dependencies
-------------------

In cases where the automatic tracking does not work, you can manually add files
to the dependencies. To do this, import the `add_dependencies` function and
call it with the filename or filenames to add:

```python
from pgfutils import setup_figure, add_dependencies, save
setup_figure(width=1, height=0.4)

# Plotting code omitted.

add_dependencies("path/to/my.file")
add_dependencies("another.file", "/absolute/path/to/a.file")
save()
```

Note that no checks are made on the filenames; it is assumed that, since your
script has used them, they are correct. Any relative filenames are assumed to
be relative to the top-level directory of the project.

[1]: http://unidata.github.io/netcdf4-python/netCDF4/index.html
