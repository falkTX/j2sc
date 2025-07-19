#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Common/Shared code
# Copyright (C) 2010-2025 Filipe Coelho <falktx@falktx.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the COPYING file

# ---------------------------------------------------------------------------------------------------------------------
# Imports (Global)

from signal import signal, SIGINT, SIGTERM

from PyQt6.QtWidgets import QApplication

# ---------------------------------------------------------------------------------------------------------------------
# Set Version

VERSION = "0.0.1"

# ---------------------------------------------------------------------------------------------------------------------
# Signal handler

def setUpSignals():
    signal(SIGINT, signalHandler)
    signal(SIGTERM, signalHandler)

def signalHandler(sig, frame):
    QApplication.instance().quit()

# ---------------------------------------------------------------------------------------------------------------------
