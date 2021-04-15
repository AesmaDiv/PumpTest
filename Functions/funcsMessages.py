from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt


def ask(title: str, text: str, accept: str = "Да", reject: str = "Нет"):
    msg: QMessageBox = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(text)
    ok = msg.addButton(accept, QMessageBox.AcceptRole)
    msg.addButton(reject, QMessageBox.RejectRole)
    msg.exec()
    return msg.clickedButton() == ok


def get(title: str, text: str, accept: str = "Добавить", reject: str = "Отмена"):
    msg: QMessageBox = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setTextInteractionFlags(Qt.TextEditable)
    ok = msg.addButton(accept, QMessageBox.AcceptRole)
    msg.addButton(reject, QMessageBox.RejectRole)
    msg.exec()
    return msg.clickedButton() == ok


def choice(title: str, text: str, choices: list):
    msg: QMessageBox = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setTextInteractionFlags(Qt.TextEditable)
    buttons = [msg.addButton(name, QMessageBox.ActionRole) for name in choices]
    msg.exec()
    return buttons.index(msg.clickedButton())


def show(title: str, *messages):
    msg: QMessageBox = QMessageBox()
    msg.setWindowTitle(title)
    message = " ".join([str(item) for item in messages])
    msg.setText(message)
    msg.exec()
