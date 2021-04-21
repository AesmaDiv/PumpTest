# from Globals.gvars import markers, wnd_pump
# from PyQt5.QtCore import QEvent, QObject, QPointF, Qt


# def process_move_marker(obj: QObject, e: QEvent.MouseMove):
#     pos: QPointF = e.pos()
#     if e.buttons() == Qt.RightButton:
#         name = 'test_lft'
#         point = markers.translatePositionToPoint(pos, 'test_lft')
#         wnd_main.txtFlow.setText('%.4f' % point.x())
#         wnd_main.txtLift.setText('%.4f' % point.y())
#     elif e.buttons() == Qt.LeftButton:
#         name = 'test_pwr'
#         point = markers.translatePositionToPoint(pos, 'test_pwr')
#         wnd_main.txtFlow.setText('%.4f' % point.x())
#         wnd_main.txtPower.setText('%.4f' % point.y())
