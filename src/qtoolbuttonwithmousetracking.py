#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2011-2025 Filipe Coelho <falktx@falktx.com>
# SPDX-License-Identifier: GPL-2.0-or-later

# ---------------------------------------------------------------------------------------------------------------------
# Imports (Global)

from PyQt6.QtWidgets import QToolButton

# ---------------------------------------------------------------------------------------------------------------------
# Widget Class

class QToolButtonWithMouseTracking(QToolButton):
    def __init__(self, parent):
        QToolButton.__init__(self, parent)
        self._font = self.font()

    def enterEvent(self, event):
        self._font.setBold(True)
        self.setFont(self._font)
        QToolButton.enterEvent(self, event)

    def leaveEvent(self, event):
        self._font.setBold(False)
        self.setFont(self._font)
        QToolButton.leaveEvent(self, event)

# ---------------------------------------------------------------------------------------------------------------------
