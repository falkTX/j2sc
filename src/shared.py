#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2010-2025 Filipe Coelho <falktx@falktx.com>
# SPDX-License-Identifier: GPL-2.0-or-later

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
