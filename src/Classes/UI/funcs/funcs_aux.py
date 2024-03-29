"""
    Модуль вспомогательных функций
"""
from time import sleep
from PyQt6.QtWidgets import QApplication
from AesmaLib.message import Message


def parseFloat(text: str):
    """безопасная конвертация строки в число с пл.запятой"""
    try:
        result = float(text)
    except (ValueError, TypeError):
        result = 0.0
    return result

def calculateEff(flw: float, lft: float, pwr: float):
    """расчёт КПД"""
    return 9.81 * lft * flw / (24 * 3600 * pwr) * 100 \
        if flw and lft and pwr else 0


def calculateEffs(flws: list, lfts: list, pwrs: list):
    """расчёт точек КПД"""
    result = []
    if checkSameLength([flws, lfts, pwrs]):
        result = [calculateEff(f,l,p) for f,l,p in zip(flws, lfts, pwrs)]
    return result

def checkSameLength(arrays: list):
    """проверка того, что массивы переданные списком имеют одинаковую длинну"""
    iterator = iter(arrays)
    length = len(next(iterator))
    return all(len(item) == length for item in iterator)


def processMouseWheel(obj, event, coef):
    """обработка события колесика мыши на полях расход-напор-мощность"""
    string = obj.text()
    val = float(string) if string else 0
    val += event.angleDelta().y() / 120 * coef
    val = round(val, 5)
    obj.setText(str(val if val >= 0 else 0))


def askPassword():
    """проверка пароля"""
    result = Message.password(
        'Внимание',
        'Необходимо подтверждение паролем:'
    ) == b'h\x87\x87\xd8\xff\x14LP,\x7f\\\xff\xaa\xfe,\xc5' \
         b'\x88\xd8`y\xf9\xde\x880L&\xb0\xcb\x99\xce\x91\xc6'
    if not result:
        Message.show("ОШИБКА", "Не верный пароль")
    return result

def pause(seconds: float):
    """задержка в секундах"""
    print(f"Пауза {seconds} секунд -> ...")
    # sleep(0.1)
    for _ in range(seconds * 1000):
        QApplication.processEvents()
        sleep(0.001)
    print("... -> продолжение")
