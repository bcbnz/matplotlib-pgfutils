import subprocess
import os
import os.path
import sys


def build_figure(working_dir, filename, environment=None):
    """Attempt to build a .pypgf image from a script.

    Parameters
    ----------
    working_dir: string
        The directory to use as the working directory when running the script.
    filename: string
        The filename of the script relative to working_dir.
    environment: dictionary, optional
        If given, any key-value pairs in this dictionary are added to the
        environment used to run the script.

    Returns
    -------
    subprocess.CompletedProcess
        The result of the attempt. The return code and anything printed to
        stdout/stderr can be accessed through this object.

    """
    # Build an environment to run it in.
    env = dict(os.environ)
    env['PYTHONPATH'] = ':'.join(os.path.normpath(p) for p in sys.path)
    env.update(environment or {})

    # Move into the desired working directory.
    cwd = os.getcwd()
    os.chdir(working_dir)

    # Run the script.
    res = subprocess.run([sys.executable, filename], text=True, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Move back into the original directory.
    os.chdir(cwd)

    # And we're done.
    return res


def build_tex(working_dir, basename, tex='xelatex'):
    """Attempt to build a PDF document from a TeX file.

    Parameters
    ----------
    working_dir: string
        The directory to use as the working directory when running TeX.
    basename: string
        The basename (i.e., without the extension) of the main TeX document,
        relative to working_dir.
    tex: string, default 'xelatex'
        The name of the TeX executable to run.

    Returns
    -------
    subprocess.CompletedProcess
        The result of the attempt. The return code and anything printed to
        stdout/stderr can be accessed through this object.

    """
    # Move into the desired working directory.
    cwd = os.getcwd()
    os.chdir(working_dir)

    # Run TeX.
    res = subprocess.run([tex, basename], text=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    # Move back into the original directory.
    os.chdir(cwd)

    # And we're done.
    return res
