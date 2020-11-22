from pgfutils import setup_figure, save
setup_figure()

import os

name1 = os.environ.get("name1", "not set")
name2 = os.environ.get("name2", "not set")

if name1 != "value1":
    raise ValueError("Incorrect value ({}) for environment variable name1".format(name1))
if name2 != "value2":
    raise ValueError("Incorrect value ({}) for environment variable name2".format(name2))

save()
