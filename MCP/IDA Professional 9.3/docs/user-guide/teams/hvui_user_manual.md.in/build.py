
import os
import sys
import glob
import logging
logger = logging.getLogger()

__dir__, __fname__ = os.path.split(__file__)
sys.path.append(os.path.join(__dir__, "..", "..", "..", "tools"))

import compose_md
composer = compose_md.composer_t()
lines = composer.compose(os.path.join(__dir__, "hvui_user_manual.md"))
with open(os.path.join("..", "hvui_user_manual.md"), "w") as fout:
    fout.writelines(lines)


# ---------------------------------------------------------------------
#
# Just for the sake of documentation how the manual used to be built,
# what follows is the contents of the makefile:
#
# TESTS_DIR ?=/tmp/${USER}

# include ../../../defaults.mk
# include ../../../allmake.mak

# HVUI_PDF := hvui_user_manual.pdf
# HVUI_HTML := hvui_user_manual.html

# all: $(HVUI_PDF) $(HVUI_HTML)

# HVUI_DEPS := hvui_user_manual.adoc makefile $(shell $(PYTHON) $(DOCTOOLS)list_deps.py --input hvui_user_manual.adoc --type adoc --ignore=refs)

# ifeq ($(NO_UPDATE_SHOTS),)
#   TARGET_IMAGES:=$(shell $(PYTHON) $(DOCTOOLS)list_deps.py --input hvui_user_manual.adoc --type image)
#   HVUI_DEPS += $(TARGET_IMAGES)
# endif

# define make-png-rule
#   $(1): $(shell $(PYTHON) ../tools/map_image_path.py --tests-base-dir $(TESTS_DIR) --adoc-rel-path $(1))
# 	$(Q)p4 edit $(1)
# 	$(Q)$(CP) $$? $(1)
# 	$(Q)p4 revert -a $(1)
# endef
# $(foreach img,$(TARGET_IMAGES),$(eval $(call make-png-rule,$(img))))

# ADOC_TOC:=

# include ../adoc.mak

# $(HVUI_PDF): $(HVUI_DEPS)
# 	$(ADOCTOR_PDF_CMD) -o $@ $<
# $(HVUI_HTML): $(HVUI_DEPS)
# 	$(ADOCTOR_HTML_CMD) -o $@ $<
