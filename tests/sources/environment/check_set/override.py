# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

import os

os.environ["name1"] = "original value"

from pgfutils import save, setup_figure

setup_figure()

import os

name1 = os.environ.get("name1", "not set")
name2 = os.environ.get("name2", "not set")

if name1 != "value1":
    raise ValueError(
        "Incorrect value ({}) for environment variable name1".format(name1)
    )
if name2 != "value2":
    raise ValueError(
        "Incorrect value ({}) for environment variable name2".format(name2)
    )

save()
