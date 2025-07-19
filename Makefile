#!/usr/bin/make -f
# Makefile for j2sc #
# ----------------- #
# Created by falkTX
#

PREFIX  = /usr/local
DESTDIR =

# -----------------------------------------------------------------------------------------------------------------------------------------

PYUIC5 ?= $(shell command -v pyuic5 2>/dev/null)
PYUIC6 ?= $(shell command -v pyuic6 2>/dev/null)

ifneq ($(PYUIC6),)
FRONTEND_TYPE = 6
else ifneq ($(PYUIC5)$(PYRCC5),)
FRONTEND_TYPE = 5
endif

ifeq ($(FRONTEND_TYPE),5)
PYUIC ?= $(PYUIC5)
else ifeq ($(FRONTEND_TYPE),6)
PYUIC ?= $(PYUIC6)
endif

# -----------------------------------------------------------------------------------------------------------------------------------------

all: UI

# -----------------------------------------------------------------------------------------------------------------------------------------
# UI code

UI: cadence

cadence: \
	src/ui_cadence.py \
	src/ui_cadence_tb_a2j.py \
	src/ui_cadence_rwait.py \
	src/ui_logs.py \
	src/ui_settings_jack.py

src/ui_%.py: resources/ui/%.ui
	$(PYUIC) $< -o $@

# -----------------------------------------------------------------------------------------------------------------------------------------

clean:
	rm -f *~ src/*~ src/*.pyc src/ui_*.py

# -----------------------------------------------------------------------------------------------------------------------------------------

install:
	# Create directories
	install -d $(DESTDIR)$(PREFIX)/bin/
	install -d $(DESTDIR)$(PREFIX)/share/applications/
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/16x16/apps/
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/48x48/apps/
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/128x128/apps/
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps/
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/
	install -d $(DESTDIR)$(PREFIX)/share/cadence/
	install -d $(DESTDIR)$(PREFIX)/share/cadence/src/
	install -d $(DESTDIR)$(PREFIX)/share/cadence/icons/

	# Install script files and binaries
	install -m 755 \
		data/cadence \
		data/cadence-jacksettings \
		data/cadence-logs \
		data/cadence-session-start \
		$(DESTDIR)$(PREFIX)/bin/

	# Install desktop files
	install -m 644 data/*.desktop $(DESTDIR)$(PREFIX)/share/applications/

	# Install icons
	install -m 644 resources/16x16/cadence.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/16x16/apps/
	install -m 644 resources/48x48/cadence.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/48x48/apps/
	install -m 644 resources/128x128/cadence.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/128x128/apps/
	install -m 644 resources/256x256/cadence.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps/
	install -m 644 resources/scalable/cadence.svg $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/

	# Install main code
	install -m 644 src/*.py $(DESTDIR)$(PREFIX)/share/cadence/src/

	# Adjust PREFIX value in script files
	sed -i "s?X-PREFIX-X?$(PREFIX)?" \
		$(DESTDIR)$(PREFIX)/bin/cadence \
		$(DESTDIR)$(PREFIX)/bin/cadence-jacksettings \
		$(DESTDIR)$(PREFIX)/bin/cadence-logs

# -----------------------------------------------------------------------------------------------------------------------------------------

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/cadence*
	rm -f $(DESTDIR)$(PREFIX)/share/applications/cadence.desktop
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/*/apps/cadence.png
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/cadence.svg
	rm -rf $(DESTDIR)$(PREFIX)/share/cadence/
