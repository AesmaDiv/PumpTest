"""
    Кастомный прогрессбар для продувки
"""

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QProgressBar


class PurgeProgress(QProgressBar):
    """Класс прогрессбара для продувки"""
    STYLESHEET = """
        PurgeProgress {
            border: 1px solid grey;
            border-radius: 2px;
            background-color: white;
        }
        PurgeProgress::chunk {
            background-color: lightblue;
            border-radius: 2px;
        }
    """
    onTick = pyqtSignal(int, name="onProgressTick")

    def __init__(self, parent=None, delay=100, *args, **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.setValue(0)
        self.setTextVisible(False)
        self.setStyleSheet(PurgeProgress.STYLESHEET)
        self._timer = QTimer(self, timeout=self.onTimeout)
        self._delay = delay
        self._offset = 1

    def start(self):
        """запуск внутреннего таймера"""
        self._timer.start(self._delay)

    def stop(self):
        """остановка внутреннего таймера"""
        self._timer.stop()
        self.setValue(0)

    def onTimeout(self):
        """колбэк таймера"""
        if self.minimum() != self.maximum():
            if self.value() <= 0:
                self._offset = 1
            if self.value() >= self.maximum():
                self._offset = -1
            self.setValue(self.value() + self._offset)
        self.onTick.emit(self.value())
        # print(self.value())
