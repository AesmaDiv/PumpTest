# from Globals.gvars import markers, wnd_pump
# from PyQt5.QtCore import QEvent, QObject, QPointF, Qt


# def process_move_marker(obj: QObject, e: QEvent.MouseMove):
#     pos: QPointF = e.pos()
#     if e.buttons() == Qt.RightButton:
#         name = 'test_lift'
#         point = markers.translatePositionToPoint(pos, 'test_lift')
#         wnd_main.txtFlow.setText('%.4f' % point.x())
#         wnd_main.txtLift.setText('%.4f' % point.y())
#     elif e.buttons() == Qt.LeftButton:
#         name = 'test_power'
#         point = markers.translatePositionToPoint(pos, 'test_power')
#         wnd_main.txtFlow.setText('%.4f' % point.x())
#         wnd_main.txtPower.setText('%.4f' % point.y())
