Workflows
=========

Environment
-----------

The general test environment is controlled by `requirements-test-apt.txt`
(system packages) and `requirements-test-pip.txt` (Python environment). Note
that matplotlib is not included in the latter -- the job will install the
version from the matrix it wants during the run.

Also note we currently pin cartopy to 0.19.0 as the latest version (0.20.0 as
of the time of writing) requires proj 8 which is not available in the Ubuntu
LTS repositories.


Locally running
---------------

The [act](https://github.com/nektos/act) project provides support for running
the workflow locally. You need to use the 'medium' image as the slim image does
not support the setup-python action. You will need to create a file `.env` with
the contents `GITHUB_TOKEN=<token>` to set an environment variable with a
GitHub token for your account. In general, you can use `act -r` to retain the
Docker containers between runs to reduce the setup time when developing
workflows.
