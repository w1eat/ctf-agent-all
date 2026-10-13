
import os
import sys
import glob
import logging
logger = logging.getLogger()

__dir__, __fname__ = os.path.split(__file__)
sys.path.append(os.path.join(__dir__, "..", "..", "tools"))

import compose_md
composer = compose_md.composer_t()
lines = composer.compose(os.path.join(__dir__, "main.md"))
with open(os.path.join("..", "teams-server.md"), "w") as fout:
    fout.writelines(lines)
