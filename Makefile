#!/usr/bin/make -f
# Makefile for Cadence #
# -------------------- #
# Created by falkTX
#

PREFIX  = /usr/local
DESTDIR =

LINK   = ln -s
PYUIC ?= pyuic5
PYRCC ?= pyrcc5

# Detect X11 rules dir
ifeq "$(wildcard /etc/X11/Xsession.d/ )" ""
	X11_RC_DIR = $(DESTDIR)/etc/X11/xinit/xinitrc.d/
else
	X11_RC_DIR = $(DESTDIR)/etc/X11/Xsession.d/
endif

# -----------------------------------------------------------------------------------------------------------------------------------------

all: RES UI

# -----------------------------------------------------------------------------------------------------------------------------------------
# Resources

RES: src/resources_rc.py

src/resources_rc.py: resources/resources.qrc
	$(PYRCC) $< -o $@

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
	rm -f *~ src/*~ src/*.pyc src/ui_*.py src/resources_rc.py

# -----------------------------------------------------------------------------------------------------------------------------------------

debug:
	$(MAKE) DEBUG=true

# -----------------------------------------------------------------------------------------------------------------------------------------

install:
	# Create directories
	install -d $(DESTDIR)/etc/xdg/autostart/
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
	install -d $(X11_RC_DIR)

	# Install script files and binaries
	install -m 755 \
		data/cadence \
		data/cadence-jacksettings \
		data/cadence-logs \
		data/cadence-render \
		data/cadence-session-start \
		$(DESTDIR)$(PREFIX)/bin/

	# Install desktop files
	install -m 644 data/autostart/*.desktop $(DESTDIR)/etc/xdg/autostart/
	install -m 644 data/*.desktop           $(DESTDIR)$(PREFIX)/share/applications/

	# Install icons
	install -m 644 resources/16x16/cadence.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/16x16/apps/
	install -m 644 resources/48x48/cadence.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/48x48/apps/
	install -m 644 resources/128x128/cadence.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/128x128/apps/
	install -m 644 resources/256x256/cadence.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/256x256/apps/
	install -m 644 resources/scalable/cadence.svg $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/

	# Install main code
	install -m 644 src/*.py $(DESTDIR)$(PREFIX)/share/cadence/src/

	# Install addtional stuff for Cadence
	install -m 755 data/61-cadence-session-inject.sh $(X11_RC_DIR)

	# Adjust PREFIX value in script files
	sed -i "s?X-PREFIX-X?$(PREFIX)?" \
		$(DESTDIR)$(PREFIX)/bin/cadence \
		$(DESTDIR)$(PREFIX)/bin/cadence-jacksettings \
		$(DESTDIR)$(PREFIX)/bin/cadence-logs \
		$(DESTDIR)$(PREFIX)/bin/cadence-session-start \
		$(X11_RC_DIR)/61-cadence-session-inject.sh

	# Delete old scripts
	rm -f $(X11_RC_DIR)/21cadence-session-inject
	rm -f $(X11_RC_DIR)/61cadence-session-inject
	rm -f $(X11_RC_DIR)/70cadence-plugin-paths
	rm -f $(X11_RC_DIR)/99cadence-session-start

# -----------------------------------------------------------------------------------------------------------------------------------------

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/cadence*
	rm -f $(DESTDIR)$(PREFIX)/share/applications/cadence.desktop
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/*/apps/cadence.png
	rm -f $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/cadence.svg
	rm -f $(DESTDIR)/etc/xdg/autostart/cadence-session-start.desktop
	rm -f $(X11_RC_DIR)/61-cadence-session-inject.sh
	rm -rf $(DESTDIR)$(PREFIX)/share/cadence/

	# Delete old scripts
	rm -f $(X11_RC_DIR)/21cadence-session-inject
	rm -f $(X11_RC_DIR)/61cadence-session-inject
	rm -f $(X11_RC_DIR)/70cadence-plugin-paths
	rm -f $(X11_RC_DIR)/99cadence-session-start
