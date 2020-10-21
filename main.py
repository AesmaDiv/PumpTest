#!/usr/bin/python3
# -*- coding: utf-8 -*-
import faulthandler
import sys

from PyQt5.QtWidgets import QApplication

import vars
from AesmaLib import Journal
from AppClasses.UI.MainWindow.MainWindow import Window as mainWindow


Journal.log(__name__, "\t*** Starting application ***")
faulthandler.enable()
app = QApplication(sys.argv)

vars.wnd_main = mainWindow()
vars.wnd_main.prepare()
vars.wnd_main.show()

app.exec_()
faulthandler.disable()
Journal.log(__name__, "\t*** Exiting application ***")
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

