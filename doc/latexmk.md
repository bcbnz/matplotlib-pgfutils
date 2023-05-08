latexmk integration
===================

[Latexmk][1] is a Perl script for running LaTeX the correct number of times to
build a document. This includes generating bibliographies, indices etc. It can
be extended to include dependencies with custom build commands.


Basic rule
----------

To create a simple rule to automatically build .pypgf figures from .py scripts,
add the following to your `latexmkrc` file:

```perl
# Build PGF images from Python scripts.
add_cus_dep('py', 'pypgf', 0, 'pypgf');
sub pypgf {
    system("python3 $_[0].py");
}
```

After inputting a figure into your document, i.e., `\input{myfig.pypgf}`,
running latexmk will result in `myfig.py` being run to create the figure. Note
that the first call that latexmk makes to latex will fail due to the missing
figure; either manually exit (in which case latexmk will continue, build the
figure, and rerun latex), or run `latexmk -interaction=nonstopmode` to let it
do this automatically.


Conditional input in TeX
------------------------

As mentioned in the previous section, a missing (i.e., not yet generated)
figure will cause an error, which latexmk will then notice. However, this only
works for a few missing files since latexmk has a limit on how many times it
will re-run before assuming a total failure has occurred. If you have many new
figures (or if you clean then rebuild), this becomes annoying. Also, the
failure can interfere with other outputs, such as writing a biblatex control
file, subsequently causing other parts of the build to fail.

One solution to this is to create a command which conditionally inputs the
figure if it exists, or prints a message if it does not exist. This allows
compilation to continue, but notifies latexmk that the figure is missing. The
following command was provided (under a different name) by the author of
latexmk in response to a [Stack Exchange question][2]:

```tex
\newcommand{\inputpypgf}[1]{%
  \InputIfFileExists{#1}{}{\typeout{No file #1.}}%
}
```

You can then use this instead of the regular `\input` macro:

```latex
\begin{figure}
  \inputpypgf{figs/measured_waveform.pypgf}
  \caption{Something we measured.}
  \label{fig:measured}
\end{figure}
```


Dependency tracking
-------------------

Internally, latexmk keeps a database of all generated files and their
dependencies. We can take advantage of pgfutils' ability to [track opened
files](file_tracking.md) to add any source data files to the dependencies, and
any rasterised images to the generated files list. This means that if you
change a data file (e.g., a saved NumPy array), the figure will be
automatically rebuilt. To do this, we need to set the `PGFUTILS_TRACK_FILES`
environment variable to 1 (track files and output a list to stdout), read the
file names and modes into an array, and then add them to the correct section of
the database based on the mode:

```perl
# Build PGF images from Python scripts, and add any dependencies
# and generated images to latexmk's database.
add_cus_dep('py', 'pypgf', 0, 'pypgf');
sub pypgf {
    # Run the script and ask pgfutils to give us a list
    # of all dependencies and extra generated files.
    my @tracked = `PGFUTILS_TRACK_FILES=1 python3 $_[0].py`;

    # Process the tracked files.
    foreach (@tracked){
        my ($mode, $fn) = /(.):(.+)/;

        # Files opened for reading: dependency.
        if($mode eq "r"){
            rdb_ensure_file($rule, $fn);
        }

        # Opened for writing: generated in addition to the .pypgf file.
        elsif($mode eq "w"){
            rdb_add_generated($fn);
        }
    }
}
```

See the [file tracking](file_tracking.md) documentation for how the tracking is
implemented and its limitations.


Loading installed support
-------------------------

The previous dependency-tracking code is included in the project source as
`data/share/matplotlib-pgfutils/latexmkrc`. If your install method copies this file into
your system, it may be preferable to execute the installed version rather than
copy-and-paste it into your `latexmkrc`. This means that, if a future version requires a
modification to this code, it will be automatically updated and included in your
project. The installation backend places it in the `share/matplotlib-pgfutils` directory
of your installation location. Under Linux, this will generally be at
`/usr/share/matplotlib-pgfutils/latexmkrc` for a system-wide install or
`~/.local/share/matplotlib-pgfutils/latexmkrc` for a user-specific install.

To load the installed copy of this code, insert the following into your
`latexmkrc`:

```perl
# Load matplotlib-pgfutils support.
my $pgfutils = "/path/to/matplotlib-pgfutils/latexmkrc";
if( !-e $pgfutils ){
    die "Could not find matplotlib-pgfutils support at $pgfutils";
}
process_rc_file($pgfutils);
```

If you have multiple users with pgfutils installed in different locations, the
following code searches a list of locations and loads the first available copy
it finds:

```perl
# Load matplotlib-pgfutils support.
my $found_pgfutils = 0;
my @pgfutils = (
    "/usr/share/matplotlib-pgfutils/latexmkrc",
    "/other/path/to/matplotlib-pgfutils/latexmkrc"
);
foreach (@pgfutils){
	if( -e $_ ){
		process_rc_file($_);
		$found_pgfutils = 1;
		last;
	}
}
if( ! $found_pgfutils ){
    die "Could not load matplotlib-pgfutils support";
}
```


Cleaning generated files
------------------------

If you set `$cleanup_includes_cusdep_generated = 1;` in your `latexmkrc`, then
any files generated by pgfutils will be removed when your ask latexmk to clean
the project directory.  In latexmk version 4.61 (and presumably older
versions), there is a bug where the extra generated files are not removed when
cleaning.  This has been fixed in version 4.63b which is included with [TeX
Live][3] 2019.  If you still have an older version of latexmk, a workaround is
to set `$cleanup_includes_generated = 1;` instead; however, this also removes
**all** generated files (including the final PDF document) when cleaning so it
may not be what you want to do.

[1]: http://personal.psu.edu/jcc8/software/latexmk/
[2]: https://tex.stackexchange.com/a/40924/7432
[3]: http://tug.org/texlive/
