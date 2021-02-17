#!/usr/bin/python3
# -*- coding: utf-8 -*-
import faulthandler
import sys

from PyQt5.QtWidgets import QApplication

from AesmaLib import journal
from Globals import gvars
from GUI.MainWindow.MainWindow import Window as mainWindow

if __name__ == '__main__':
    journal.log(__name__, '\t', "*** Starting application ***")
    faulthandler.enable()
    app = QApplication(sys.argv)

    gvars.wnd_main = mainWindow()
    gvars.wnd_main.prepare()
    gvars.wnd_main.show()

    app.exec_()
    faulthandler.disable()
    journal.log(__name__, '\t', "*** Exiting application ***")

# adam = Adam5K('10.10.10.10', 502, 1)
# adam.connect()
# adam.setReadingThread(True)
# adam.setSlot(Adam5K.SlotType.DIGITAL, 0, [True] * 8 * 4)
# adam.setSlot(Adam5K.SlotType.DIGITAL, 3, [True] * 8 * 4)
# while adam.isBusy():
#     sleep(1.5)
#     pass
# adam.setReadingThread(False)
# adam.disconnect(False)
