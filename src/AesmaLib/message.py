"""
    Модуль содержит функции диалоговых окон"""
import hashlib
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QLineEdit
from PyQt6.QtCore import Qt

class Message:
    """Класс вывода диалоговых окон"""
    @staticmethod
    def ask(title: str, text: str, accept: str = "Да", reject: str = "Нет"):
        """вывод окна с запросом типа да/нет"""
        msg: QMessageBox = QMessageBox()
        msg.setStyleSheet("""
        QMessageBox QLabel {
            padding: 10px;
        }
        """)
        msg.setWindowTitle(title)
        msg.setText(text)
        is_ok = msg.addButton(accept, QMessageBox.ButtonRole.AcceptRole)
        msg.addButton(reject, QMessageBox.ButtonRole.RejectRole)
        msg.exec()
        return msg.clickedButton() == is_ok

    @staticmethod
    def get(title: str, text: str, accept: str = "Добавить", reject: str = "Отмена"):
        """вывод окна с запросом типа добавить/отмена"""
        msg: QMessageBox = QMessageBox()
        msg.setStyleSheet("""
        QMessageBox QLabel {
            padding: 10px;
        }
        """)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditable)
        is_ok = msg.addButton(accept, QMessageBox.ButtonRole.AcceptRole)
        msg.addButton(reject, QMessageBox.ButtonRole.RejectRole)
        msg.exec()
        return msg.clickedButton() == is_ok

    @staticmethod
    def choice(title: str, text: str, choices: list):
        """вывод окна с выбором из нескольких вариантов"""
        msg: QMessageBox = QMessageBox()
        msg.setStyleSheet("""
        QMessageBox QLabel {
            padding: 10px;
        }
        """)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditable)
        buttons = [msg.addButton(name, QMessageBox.ButtonRole.ActionRole) for name in choices]
        msg.exec()
        return buttons.index(msg.clickedButton())

    @staticmethod
    def password(title: str, text: str):
        """вывод окна с полем ввода"""
        msg = QInputDialog()
        hash_func = hashlib.sha256()
        hash_func.update(
            msg.getText(
                None, title, text, echo=QLineEdit.EchoMode.Password
            )[0].encode('utf-8')
        )
        result = hash_func.digest()
        return result


    @staticmethod
    def show(title: str, *messages):
        """вывод окна с сообщением"""
        msg: QMessageBox = QMessageBox()
        msg.setStyleSheet("""
        QMessageBox QLabel {
            padding: 10px;
        }
        """)
        msg.setWindowTitle(title)
        message = " ".join([str(item) for item in messages])
        msg.setText(message)
        msg.exec()
