
import os
import sys
import glob
import logging
logger = logging.getLogger()


__dir__, __fname__ = os.path.split(__file__)

#
# 1) Generate `refs/`, from `refs.in/`
#

refs_dir = os.path.join(__dir__, "refs")
assert(not os.path.exists(refs_dir))
os.makedirs(refs_dir)

sys.path.append(os.path.join(__dir__, "..", "..", "..", "tools"))
import cd2adoc_base

class converter_t(cd2adoc_base.converter_t):
    def __init__(self, logger):
        super().__init__(logger)
        self.css_subst = [
            ("$ARGUMENT", r"[%s](#local-path)"),     # possibly substitute for a more appropriate CSS name
        ]

    def _looks_like_link(self, thing):
        if super()._looks_like_link(thing):
            return True
        return thing.startswith("[") and thing.endswith(")...") and thing.find("](") > -1

    def substitutions_in_params(self, text):
        return self._substitutions_in_params(text, self.css_subst)

    def substitutions_in_options(self, text):
        return self.substitutions_in_params(text)

    def substitutions_in_examples(self, text):
        if text.startswith("$$"):
            text = "alice@alice_PC$ lc %s %s" % (self.user_command, text[2:].lstrip())
        elif text.startswith("$"):
            text = "alice@alice_PC$ %s" % text[1:].lstrip()
        return text

for src_cd in glob.glob(os.path.join("refs.in", "*.cd")):
    _, target_fname = os.path.split(src_cd)
    target_fname = target_fname.replace(".cd", ".md")
    target_adoc = os.path.join(refs_dir, target_fname)
    cvt = converter_t(logger)
    cvt.convert(src_cd, target_adoc)

#
# 2) Compose the final markdown, using the silly composer tool
#

import compose_md
composer = compose_md.composer_t()
lines = composer.compose(os.path.join(__dir__, "lc_user_manual.md"))
with open(os.path.join("..", "lc_user_manual.md"), "w") as fout:
    fout.writelines(lines)
