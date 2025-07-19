#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# JACK2 Simple Configurator
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

from PyQt6.QtCore import pyqtSlot, Qt, QProcess, QSemaphore, QSettings, QThread, QTimer
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow

# ------------------------------------------------------------------------------------------------------------
# Imports (Custom Stuff)

from shared import *

import settings
import ui_j2sc
import ui_j2sc_tb_a2j
import ui_j2sc_rwait

# ------------------------------------------------------------------------------------------------------------
# Try Import DBus

try:
    import dbus
    from dbus.mainloop.pyqt5 import DBusQtMainLoop as DBusMainLoop
    haveDBus = True
except:
    try:
        # Try falling back to GMainLoop
        from dbus.mainloop.glib import DBusGMainLoop as DBusMainLoop
        haveDBus = True
    except:
        haveDBus = False

# ------------------------------------------------------------------------------------------------------------
# Get Process list

def getProcList():
    retProcs = []

    if HAIKU or LINUX or MACOS:
        process = QProcess()
        process.start("ps", ["-u", str(os.getuid())])
        process.waitForFinished()

        processDump = process.readAllStandardOutput().split("\n")

        for i in range(len(processDump)):
            if (i == 0): continue
            dumpTest = str(processDump[i], encoding="utf-8").rsplit(":", 1)[-1].split(" ")
            if len(dumpTest) > 1 and dumpTest[1]:
                retProcs.append(dumpTest[1])

    else:
        print("getProcList() - Not supported in this system")

    return retProcs

# ------------------------------------------------------------------------------------------------------------
# Stop all audio processes, used for force-restart

def waitProcsEnd(procs, tries):
    for x in range(tries):
        procsList = getProcList()
        for proc in procs:
            if proc in procsList:
                break
            else:
                sleep(0.1)
        else:
            break

# ------------------------------------------------------------------------------------------------------------
# Cleanly close the jack dbus service

def tryCloseJackDBus():
    try:
        import dbus
        bus = dbus.SessionBus()
        jack = bus.get_object("org.jackaudio.service", "/org/jackaudio/Controller")
        jack.Exit()
    except:
        print("tryCloseJackDBus() failed")

# ------------------------------------------------------------------------------------------------------------
# Stop all audio processes, used for force-restart

def stopAllAudioProcesses(tryCloseJack = True):
    if tryCloseJack:
        tryCloseJackDBus()

    if not (HAIKU or LINUX or MACOS):
        print("stopAllAudioProcesses() - Not supported in this system")
        return

    process = QProcess()

    procsTerm = ["a2j", "a2jmidid", "artsd", "jackd", "jackdmp", "knotify4", "lash", "ladishd", "ladiappd", "ladiconfd", "jmcore"]
    procsKill = ["jackdbus", "pulseaudio"]
    tries     = 20

    process.start("killall", procsTerm)
    process.waitForFinished()
    waitProcsEnd(procsTerm, tries)

    process.start("killall", ["-KILL"] + procsKill)
    process.waitForFinished()
    waitProcsEnd(procsKill, tries)

# ---------------------------------------------------------------------

# Wait while JACK restarts
class ForceRestartThread(QThread):
    progressChanged = pyqtSignal(int)

    def __init__(self, parent):
        QThread.__init__(self, parent)

        self.m_wasStarted = False

    def wasJackStarted(self):
        return self.m_wasStarted

    def startA2J(self):
        if not gDBus.a2j.get_hw_export() and QSettings().value("A2J/AutoExport", True, type=bool):
            gDBus.a2j.set_hw_export(True)
        gDBus.a2j.start()

    def run(self):
        # Not started yet
        self.m_wasStarted = False
        self.progressChanged.emit(0)

        # Stop JACK safely first, if possible
        runFunctionInMainThread(tryCloseJackDBus)
        self.progressChanged.emit(20)

        # Kill All
        stopAllAudioProcesses(False)
        self.progressChanged.emit(30)

        # Connect to jackdbus
        runFunctionInMainThread(self.parent().DBusReconnect)

        if not gDBus.jack:
            return

        for x in range(30):
            self.progressChanged.emit(30+x*2)
            procsList = getProcList()
            if "jackdbus" in procsList:
                break
            else:
                sleep(0.1)

        self.progressChanged.emit(90)

        # Start it
        runFunctionInMainThread(gDBus.jack.StartServer)
        self.progressChanged.emit(93)

        # If we made it this far, then JACK is started
        self.m_wasStarted = True

        # Start bridges according to user settings

        self.progressChanged.emit(94)

        # ALSA-MIDI
        if QSettings().value("A2J/AutoStart", True, type=bool) and gDBus.a2j and not bool(gDBus.a2j.is_started()):
            runFunctionInMainThread(self.startA2J)

        self.progressChanged.emit(100)

# Force Restart Dialog
class ForceWaitDialog(QDialog, ui_j2sc_rwait.Ui_Dialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Dialog|Qt.WindowCloseButtonHint)

        self.rThread = ForceRestartThread(self)
        self.rThread.start()

        self.rThread.progressChanged.connect(self.progressBar.setValue)
        self.rThread.finished.connect(self.slot_rThreadFinished)

    def DBusReconnect(self):
        self.parent().DBusReconnect()

    @pyqtSlot()
    def slot_rThreadFinished(self):
        self.close()

        if self.rThread.wasJackStarted():
            QMessageBox.information(self, self.tr("Info"), self.tr("JACK was re-started sucessfully"))
        else:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Could not start JACK!"))

    def done(self, r):
        QDialog.done(self, r)
        self.close()

# Main Window
class CadenceMainW(QMainWindow, ui_j2sc.Ui_CadenceMainW):
    DBusJackServerStartedCallback = pyqtSignal()
    DBusJackServerStoppedCallback = pyqtSignal()
    DBusA2JBridgeStartedCallback = pyqtSignal()
    DBusA2JBridgeStoppedCallback = pyqtSignal()

    SIGTERM = pyqtSignal()
    SIGUSR1 = pyqtSignal()
    SIGUSR2 = pyqtSignal()

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.loadSettings(True)

        self.pix_apply   = QIcon(getIcon("dialog-ok-apply", 16)).pixmap(16, 16)
        self.pix_cancel  = QIcon(getIcon("dialog-cancel", 16)).pixmap(16, 16)
        self.pix_error   = QIcon(getIcon("dialog-error", 16)).pixmap(16, 16)

        self.b_jack_switchmaster.setEnabled(False)

        # -------------------------------------------------------------
        # Set-up connections

        self.b_jack_start.clicked.connect(self.slot_JackServerStart)
        self.b_jack_stop.clicked.connect(self.slot_JackServerStop)
        self.b_jack_restart.clicked.connect(self.slot_JackServerForceRestart)
        self.b_jack_configure.clicked.connect(self.slot_JackServerConfigure)
        self.b_jack_switchmaster.clicked.connect(self.slot_JackServerSwitchMaster)

        self.b_a2j_start.clicked.connect(self.slot_A2JBridgeStart)
        self.b_a2j_stop.clicked.connect(self.slot_A2JBridgeStop)

        # org.jackaudio.JackControl
        self.DBusJackServerStartedCallback.connect(self.slot_DBusJackServerStartedCallback)
        self.DBusJackServerStoppedCallback.connect(self.slot_DBusJackServerStoppedCallback)

        # org.gna.home.a2jmidid.control
        self.DBusA2JBridgeStartedCallback.connect(self.slot_DBusA2JBridgeStartedCallback)
        self.DBusA2JBridgeStoppedCallback.connect(self.slot_DBusA2JBridgeStoppedCallback)
        self.cb_a2j_autoexport.stateChanged[int].connect(self.slot_A2JBridgeExportHW)

        # -------------------------------------------------------------

        self.m_last_dsp_load = None
        self.m_last_xruns    = None
        self.m_last_buffer_size = None

        self.m_timer500  = None
        self.m_timer2000 = self.startTimer(2000)

        self.DBusReconnect()

        if haveDBus:
            gDBus.bus.add_signal_receiver(self.DBusSignalReceiver, destination_keyword='dest', path_keyword='path',
                member_keyword='member', interface_keyword='interface', sender_keyword='sender', )

        # keep application responsive, otherwise Ctrl+C does nothing
        self.startTimer(100)

    def DBusReconnect(self):
        if haveDBus:
            try:
                gDBus.jack     = gDBus.bus.get_object("org.jackaudio.service", "/org/jackaudio/Controller")
                gDBus.patchbay = dbus.Interface(gDBus.jack, "org.jackaudio.JackPatchbay")
                settings.initBus(gDBus.bus)
            except:
                gDBus.jack     = None
                gDBus.patchbay = None

            try:
                gDBus.a2j = dbus.Interface(gDBus.bus.get_object("org.gna.home.a2jmidid", "/"), "org.gna.home.a2jmidid.control")
            except:
                gDBus.a2j = None

        if gDBus.jack:
            if gDBus.jack.IsStarted():
                self.jackStarted()

            else:
                self.jackStopped()
                self.label_jack_realtime.setText("Yes" if settings.isRealtime() else "No")
        else:
            self.jackStopped()
            self.label_jack_status.setText("Unavailable")
            self.label_jack_status_ico.setPixmap(self.pix_error)
            self.label_jack_realtime.setText("Unknown")
            self.label_jack_realtime_ico.setPixmap(self.pix_error)
            self.groupBox_jack.setEnabled(False)
            self.groupBox_jack.setTitle("-- jackdbus is not available --")
            self.b_jack_start.setEnabled(False)
            self.b_jack_stop.setEnabled(False)
            self.b_jack_restart.setEnabled(False)
            self.b_jack_configure.setEnabled(False)
            self.b_jack_switchmaster.setEnabled(False)
            self.toolBox_alsamidi.setEnabled(False)

        if gDBus.a2j:
            try:
                started = gDBus.a2j.is_started()
            except:
                started = False

            if started:
                self.a2jStarted()
            else:
                self.a2jStopped()
        else:
            self.toolBox_alsamidi.setEnabled(False)
            self.cb_a2j_autostart.setChecked(False)
            self.cb_a2j_autoexport.blockSignals(True)
            self.cb_a2j_autoexport.setChecked(False)
            self.cb_a2j_autoexport.blockSignals(False)
            self.label_bridge_a2j.setText("ALSA MIDI Bridge is not installed")
            QSettings().setValue("A2J/AutoStart", False)

    def DBusSignalReceiver(self, *args, **kwds):
        if kwds['interface'] == "org.freedesktop.DBus" and kwds['path'] == "/org/freedesktop/DBus" and kwds['member'] == "NameOwnerChanged":
            appInterface, appId, newId = args

            if not newId:
                # Something crashed
                if appInterface == "org.jackaudio.service":
                    QTimer.singleShot(0, self.slot_handleCrash_jack)
                elif appInterface == "org.gna.home.a2jmidid":
                    QTimer.singleShot(0, self.slot_handleCrash_a2j)

        elif kwds['interface'] == "org.jackaudio.JackControl":
            if DEBUG: print("org.jackaudio.JackControl", kwds['member'])
            if kwds['member'] == "ServerStarted":
                self.DBusJackServerStartedCallback.emit()
            elif kwds['member'] == "ServerStopped":
                self.DBusJackServerStoppedCallback.emit()

        elif kwds['interface'] == "org.gna.home.a2jmidid.control":
            if DEBUG: print("org.gna.home.a2jmidid.control", kwds['member'])
            if kwds['member'] == "bridge_started":
                self.DBusA2JBridgeStartedCallback.emit()
            elif kwds['member'] == "bridge_stopped":
                self.DBusA2JBridgeStoppedCallback.emit()

    def jackStarted(self):
        self.m_last_dsp_load = gDBus.jack.GetLoad()
        self.m_last_xruns    = int(gDBus.jack.GetXruns())
        self.m_last_buffer_size = gDBus.jack.GetBufferSize()

        self.b_jack_start.setEnabled(False)
        self.b_jack_stop.setEnabled(True)
        self.b_jack_switchmaster.setEnabled(True)

        self.label_jack_status.setText("Started")
        self.label_jack_status_ico.setPixmap(self.pix_apply)

        if gDBus.jack.IsRealtime():
            self.label_jack_realtime.setText("Yes")
            self.label_jack_realtime_ico.setPixmap(self.pix_apply)
        else:
            self.label_jack_realtime.setText("No")
            self.label_jack_realtime_ico.setPixmap(self.pix_cancel)

        self.label_jack_dsp.setText("%.2f%%" % self.m_last_dsp_load)
        self.label_jack_xruns.setText(str(self.m_last_xruns))
        self.label_jack_bfsize.setText("%i samples" % self.m_last_buffer_size)
        self.label_jack_srate.setText("%i Hz" % gDBus.jack.GetSampleRate())
        self.label_jack_latency.setText("%.1f ms" % gDBus.jack.GetLatency())

        self.m_timer500 = self.startTimer(500)

        if gDBus.a2j and not gDBus.a2j.is_started():
            portsExported = bool(gDBus.a2j.get_hw_export())
            settings = QSettings()
            if settings.value("A2J/AutoStart", True, type=bool):
                if not portsExported and settings.value("A2J/AutoExport", True, type=bool):
                    gDBus.a2j.set_hw_export(True)
                    portsExported = True
                gDBus.a2j.start()
            else:
                self.b_a2j_start.setEnabled(True)

    def jackStopped(self):
        if self.m_timer500:
            self.killTimer(self.m_timer500)
            self.m_timer500 = None

        self.m_last_dsp_load = None
        self.m_last_xruns    = None
        self.m_last_buffer_size = None

        self.b_jack_start.setEnabled(True)
        self.b_jack_stop.setEnabled(False)
        self.b_jack_switchmaster.setEnabled(False)

        self.label_jack_status.setText("Stopped")
        self.label_jack_status_ico.setPixmap(self.pix_cancel)

        self.label_jack_dsp.setText("---")
        self.label_jack_xruns.setText("---")
        self.label_jack_bfsize.setText("---")
        self.label_jack_srate.setText("---")
        self.label_jack_latency.setText("---")

        if gDBus.a2j:
            self.b_a2j_start.setEnabled(False)

    def a2jStarted(self):
        self.b_a2j_start.setEnabled(False)
        self.b_a2j_stop.setEnabled(True)
        if bool(gDBus.a2j.get_hw_export()):
            self.label_bridge_a2j.setText(self.tr("ALSA MIDI Bridge is running, ports are exported"))
        else :
            self.label_bridge_a2j.setText(self.tr("ALSA MIDI Bridge is running"))

    def a2jStopped(self):
        jackRunning = bool(gDBus.jack and gDBus.jack.IsStarted())
        self.b_a2j_start.setEnabled(jackRunning)
        self.b_a2j_stop.setEnabled(False)
        self.label_bridge_a2j.setText(self.tr("ALSA MIDI Bridge is stopped"))

    @pyqtSlot()
    def func_start_logs(self):
        self.func_start_tool("cadence-logs")

    def func_start_tool(self, tool):
        if sys.argv[0].endswith(".py"):
            if tool == "cadence-logs":
                tool = "logs"
            elif tool == "cadence-render":
                tool = "render"

            python = sys.executable
            tool  += ".py"
            base   = sys.argv[0].rsplit("cadence.py", 1)[0]

            if python:
                python += " "

            cmd = "%s%s%s &" % (python, base, tool)

            print(cmd)
            os.system(cmd)

        elif sys.argv[0].endswith("/cadence"):
            base = sys.argv[0].rsplit("/cadence", 1)[0]
            os.system("%s/%s &" % (base, tool))

        else:
            os.system("%s &" % tool)

    @pyqtSlot()
    def slot_DBusJackServerStartedCallback(self):
        self.jackStarted()

    @pyqtSlot()
    def slot_DBusJackServerStoppedCallback(self):
        self.jackStopped()

    @pyqtSlot()
    def slot_DBusA2JBridgeStartedCallback(self):
        self.a2jStarted()

    @pyqtSlot()
    def slot_DBusA2JBridgeStoppedCallback(self):
        self.a2jStopped()

    @pyqtSlot()
    def slot_JackServerStart(self):
        self.saveSettings()
        try:
            gDBus.jack.StartServer()
        except:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Failed to start JACK, please check the logs for more information."))

    @pyqtSlot()
    def slot_JackServerStop(self):
        if gDBus.a2j and bool(gDBus.a2j.is_started()):
            gDBus.a2j.stop()
        try:
            gDBus.jack.StopServer()
        except:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Failed to stop JACK, please check the logs for more information."))

    @pyqtSlot()
    def slot_JackServerForceRestart(self):
        if gDBus.jack.IsStarted():
            ask = CustomMessageBox(self, QMessageBox.Icon.Warning, self.tr("Warning"),
                                   self.tr("This will force kill all JACK applications!<br>Make sure to save your projects before continue."),
                                   self.tr("Are you sure you want to force the restart of JACK?"))

            if ask != QMessageBox.StandardButton.Yes:
                return

        if self.m_timer500:
            self.killTimer(self.m_timer500)
            self.m_timer500 = None

        self.saveSettings()
        ForceWaitDialog(self).exec_()

    @pyqtSlot()
    def slot_JackServerConfigure(self):
        settings.JackSettingsW(self).exec()

    @pyqtSlot()
    def slot_JackServerSwitchMaster(self):
        try:
            gDBus.jack.SwitchMaster()
        except:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Failed to switch JACK master, please check the logs for more information."))
            return

        self.jackStarted()

    @pyqtSlot()
    def slot_JackClearXruns(self):
        if gDBus.jack:
            gDBus.jack.ResetXruns()

    @pyqtSlot()
    def slot_A2JBridgeStart(self):
        gDBus.a2j.start()

    @pyqtSlot()
    def slot_A2JBridgeStop(self):
        gDBus.a2j.stop()

    @pyqtSlot(int)
    def slot_A2JBridgeExportHW(self, state):
        a2jWasStarted = bool(gDBus.a2j.is_started())

        if a2jWasStarted:
            gDBus.a2j.stop()

        gDBus.a2j.set_hw_export(bool(state))

        if a2jWasStarted:
            gDBus.a2j.start()

    @pyqtSlot()
    def slot_handleCrash_jack(self):
        self.DBusReconnect()

    @pyqtSlot()
    def slot_handleCrash_a2j(self):
        pass

    def saveSettings(self):
        settings = QSettings()
        settings.setValue("Geometry", self.saveGeometry())
        settings.setValue("A2J/AutoStart", self.cb_a2j_autostart.isChecked())
        settings.setValue("A2J/AutoExport", self.cb_a2j_autoexport.isChecked())

    def loadSettings(self, geometry):
        settings = QSettings()

        if geometry:
            self.restoreGeometry(settings.value("Geometry", b""))

        self.cb_a2j_autostart.setChecked(settings.value("A2J/AutoStart", True, type=bool))
        self.cb_a2j_autoexport.setChecked(settings.value("A2J/AutoExport", True, type=bool))

    def timerEvent(self, event):
        if event.timerId() == self.m_timer500:
            if gDBus.jack and gDBus.jack.IsStarted() and self.m_last_dsp_load != None:
                next_dsp_load = gDBus.jack.GetLoad()
                next_xruns    = int(gDBus.jack.GetXruns())

                if self.m_last_dsp_load != next_dsp_load:
                    self.m_last_dsp_load = next_dsp_load
                    self.label_jack_dsp.setText("%.2f%%" % self.m_last_dsp_load)

                if self.m_last_xruns != next_xruns:
                    self.m_last_xruns = next_xruns
                    self.label_jack_xruns.setText(str(self.m_last_xruns))

        elif event.timerId() == self.m_timer2000:
            if gDBus.jack and gDBus.jack.IsStarted() and self.m_last_buffer_size != None:
                next_buffer_size = gDBus.jack.GetBufferSize()

                if self.m_last_buffer_size != next_buffer_size:
                    self.m_last_buffer_size = next_buffer_size
                    self.label_jack_bfsize.setText("%i samples" % self.m_last_buffer_size)
                    self.label_jack_latency.setText("%.1f ms" % gDBus.jack.GetLatency())

            else:
                self.update()

        QMainWindow.timerEvent(self, event)

    def closeEvent(self, event):
        self.saveSettings()

# ------------------------------------------------------------------------------------------------------------

def runFunctionInMainThread(task):
    waiter = QSemaphore(1)

    def taskInMainThread():
        task()
        waiter.release()

    QTimer.singleShot(0, taskInMainThread)
    waiter.tryAcquire()

#--------------- main ------------------
if __name__ == '__main__':
    # App initialization
    app = QApplication(sys.argv)
    app.setApplicationName("J2SC")
    app.setApplicationVersion(VERSION)
    app.setDesktopFileName("j2sc")
    app.setOrganizationName("falkTX")
    # app.setWindowIcon(QIcon(":/scalable/cadence.svg"))

    if haveDBus:
        gDBus.loop = DBusMainLoop(set_as_default=True)
        gDBus.bus = dbus.SessionBus(mainloop=gDBus.loop)

    # Show GUI
    gui = CadenceMainW()

    # Set-up custom signal handling
    setUpSignals(gui)

    gui.show()

    # Exit properly
    sys.exit(app.exec())
