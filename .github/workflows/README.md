<!--
SPDX-FileCopyrightText: Blair Bonnett
SPDX-License-Identifier: BSD-3-Clause
-->

Workflows
=========

Environment
-----------

The general test environment is controlled by `requirements-test-apt.txt`
(system packages) and `requirements-test-pip.txt` (Python environment). Note
that matplotlib is not included in the latter -- the job will install the
version from the matrix it wants during the run.


Locally running
---------------

The [act](https://github.com/nektos/act) project provides support for running
the workflow locally. You need to use the 'medium' image as the slim image does
not support the setup-python action. You will need to create a file `.secrets` with
the contents `GITHUB_TOKEN=<token>` to specify an GitHub token for your
account. In general, you can use `act -r` to retain the Docker containers
between runs to reduce the setup time when developing workflows.
