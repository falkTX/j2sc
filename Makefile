#!/usr/bin/make -f
# Makefile for j2sc #
# ----------------- #
# Created by falkTX
#

PREFIX  = /usr/local
DESTDIR =

# -----------------------------------------------------------------------------------------------------------------------------------------

all: UI

# -----------------------------------------------------------------------------------------------------------------------------------------
# UI code

UI: \
	src/ui_j2sc.py \
	src/ui_j2sc_tb_a2j.py \
	src/ui_j2sc_rwait.py \
	src/ui_logs.py \
	src/ui_settings.py

src/ui_%.py: resources/ui/%.ui
	pyuic6 $< -o $@

# -----------------------------------------------------------------------------------------------------------------------------------------

clean:
	rm -f src/*.pyc src/ui_*.py

# -----------------------------------------------------------------------------------------------------------------------------------------

install:
	# Create directories
	install -d $(DESTDIR)$(PREFIX)/bin
	install -d $(DESTDIR)$(PREFIX)/share/applications
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/16x16/apps
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/48x48/apps
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/128x128/apps
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps
	install -d $(DESTDIR)$(PREFIX)/share/j2sc

	# Install script files and binaries
	install -m 755 \
		data/j2sc \
		data/j2sc-logs \
		data/j2sc-settings \
		$(DESTDIR)$(PREFIX)/bin/

	# Install desktop files
	install -m 644 data/*.desktop $(DESTDIR)$(PREFIX)/share/applications/

	# Install icons
	install -m 644 resources/16x16/j2sc.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/16x16/apps/
	install -m 644 resources/48x48/j2sc.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/48x48/apps/
	install -m 644 resources/128x128/j2sc.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/128x128/apps/
	install -m 644 resources/256x256/j2sc.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps/
	install -m 644 resources/scalable/j2sc.svg $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/

	# Install python code
	install -m 644 src/*.py $(DESTDIR)$(PREFIX)/share/j2sc/

	# Adjust PREFIX value in script files
	sed -i "s?X-PREFIX-X?$(PREFIX)?" \
		$(DESTDIR)$(PREFIX)/bin/j2sc \
		$(DESTDIR)$(PREFIX)/bin/j2sc-logs \
		$(DESTDIR)$(PREFIX)/bin/j2sc-settings \
		$(DESTDIR)$(PREFIX)/share/j2sc/*.py

# -----------------------------------------------------------------------------------------------------------------------------------------

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/j2sc*
	rm -f $(DESTDIR)$(PREFIX)/share/applications/j2sc.desktop
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/*/apps/j2sc.png
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/j2sc.svg
	rm -rf $(DESTDIR)$(PREFIX)/share/j2sc/
