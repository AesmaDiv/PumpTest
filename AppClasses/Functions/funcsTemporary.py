from PyQt5.QtCore import Qt, QEvent, QObject, QPointF

import vars


def process_move_marker(obj: QObject, e: QEvent.MouseMove):
    pos: QPointF = e.pos()
    if e.buttons() == Qt.RightButton:
        name = 'test_lift'
        point = vars.markers.translatePositionToPoint(pos, 'test_lift')
        vars.wnd_main.txtFlow.setText('%.4f' % point.x())
        vars.wnd_main.txtLift.setText('%.4f' % point.y())
    elif e.buttons() == Qt.LeftButton:
        name = 'test_power'
        point = vars.markers.translatePositionToPoint(pos, 'test_power')
        vars.wnd_main.txtFlow.setText('%.4f' % point.x())
        vars.wnd_main.txtPower.setText('%.4f' % point.y())
