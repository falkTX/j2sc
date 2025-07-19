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

# ------------------------------------------------------------------------------------------------------------
# Imports (Global)

import os
import sys

from signal import signal, SIGINT, SIGTERM

from PyQt6.QtCore import pyqtSignal, qWarning
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox

# ------------------------------------------------------------------------------------------------------------
# Set Version

VERSION = "0.9.2"

# ------------------------------------------------------------------------------------------------------------
# Global variables

global gGui
gGui = None

# ------------------------------------------------------------------------------------------------------------
# Signal handler

def setUpSignals(self_):
    global gGui

    if gGui is None:
        gGui = self_

    signal(SIGINT, signalHandler)
    signal(SIGTERM, signalHandler)

    gGui.SIGTERM.connect(closeWindowHandler)

def signalHandler(sig, frame):
    global gGui

    if gGui is None:
        return

    if sig in (SIGINT, SIGTERM):
        gGui.SIGTERM.emit()

def closeWindowHandler():
    global gGui

    if gGui is None:
        return

    gGui.hide()
    gGui.close()
    QApplication.instance().quit()

    gGui = None
