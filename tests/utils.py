from contextlib import contextmanager
import os
from pathlib import Path
import subprocess
import sys


def clean_directory(path, mode="all"):
    """Remove files built as part of a test from a directory.

    Parameters
    ----------
    path : path-like
        The path to the directory to clean.
    mode : {"all", "pypgf", "tex"}
        Which types of file to clean.

    """
    for fn in Path(path).iterdir():
        if not fn.is_file():
            continue

        if mode in {"tex", "all"}:
            if fn.suffix in {".aux", ".log", ".pdf"}:
                fn.unlink()

        elif mode in {"pypgf", "all"}:
            if fn.suffix in {".png", ".pypgf"} or fn.name == "tracking.test.results":
                fn.unlink()


@contextmanager
def build_pypgf(figure_dir, filename, environment=None):
    """Build a .pypgf figure from a script.

    This context manager will remove the figure and any related files (such as included
    PNGs) when it exits.

    Parameters
    ----------
    figure_dir : path-like
        Directory containing the script. The output will be placed in this directory
        also.
    filename : string
        The name of the script within the given directory.
    environment: dictionary, optional
        If given, any key-value pairs in this dictionary are added to the current
        environment when running the script.

    Yields
    ------
    result : subprocess.CompletedProcess
        The result of the sub-process used to run the script. The returncode attribute
        indicates the exit status of the process, while the stdout and stderr attribute
        have strings captured the corresponding stream. These streams are echoed to the
        main process streams.

    """
    # Get any specified paths and add all paths in this process.
    environment = environment or {}
    paths = environment.pop("PYTHONPATH", "").split(":")
    paths.extend(str(Path(p).resolve()) for p in sys.path)

    # Generate the sub-environment.
    env = dict(os.environ)
    env["PYTHONPATH"] = ":".join(paths)
    env.update(environment)

    # Run the script.
    res = subprocess.run(
        [sys.executable, filename],
        capture_output=True,
        text=True,
        env=env,
        cwd=figure_dir,
    )

    # Echo the output streams.
    sys.stdout.write(res.stdout)
    sys.stdout.flush()
    sys.stderr.write(res.stderr)
    sys.stderr.flush()

    # Pass the result to the user, and clean up afterwards.
    try:
        yield res
    finally:
        clean_directory(figure_dir, mode="pypgf")


@contextmanager
def build_tex(doc_dir, basename, tex="xelatex"):
    """Attempt to build a PDF document from a TeX file.

    This context manager will remove the PDF and any auxiliary TeX files when it exits.
    PNGs) when it exits.

    Parameters
    ----------
    doc_dir: path-like
        The directory containing the document to build.
    basename: string
        The basename (i.e., without the extension) of the main TeX document, relative to
        working_dir.
    tex: string, default 'xelatex'
        The name of the TeX executable to run.

    Yields
    ------
    subprocess.CompletedProcess
        The result of the sub-process used to run TeX. The returncode attribute
        indicates the exit status of the process, while the stdout and stderr attribute
        have strings captured the corresponding stream. These streams are echoed to the
        main process streams.

    """
    # Run TeX.
    res = subprocess.run([tex, basename], capture_output=True, text=True, cwd=doc_dir)

    # Echo the output streams.
    sys.stdout.write(res.stdout)
    sys.stdout.flush()
    sys.stderr.write(res.stderr)
    sys.stderr.flush()

    # Pass the result to the user, and clean up afterwards.
    try:
        yield res
    finally:
        clean_directory(doc_dir, mode="tex")


@contextmanager
def in_directory(dirname):
    """Context manager to run code within a directory.

    This changes the working directory to a specified path when the context manager
    starts, and returns to the original working directory when it exits.

    Parameters
    ----------
    dirname : path-like
        The directory to run in.

    """
    pwd = Path.cwd()
    os.chdir(dirname)
    try:
        yield
    finally:
        os.chdir(pwd)
