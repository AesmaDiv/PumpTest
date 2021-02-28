"""
    AesmaDiv 2021
    Программа для стенда испытания ЭЦН
"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-
import faulthandler
import sys

from PyQt5.QtWidgets import QApplication

from AesmaLib.journal import Journal
from Globals import gvars


if __name__ == '__main__':
    Journal.log(__name__, '\t', "*** Starting application ***")
    faulthandler.enable()
    app = QApplication(sys.argv)

    gvars.wnd_main = gvars.MainWindow()
    gvars.wnd_main.prepare()
    gvars.wnd_main.show()

    app.exec_()
    faulthandler.disable()
    Journal.log(__name__, '\t', "*** Exiting application ***")
