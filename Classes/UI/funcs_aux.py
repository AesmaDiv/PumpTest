"""
    Модуль вспомогательных функций
"""
from datetime import datetime
from AesmaLib.message import Message


def parse_float(text: str):
    """ безопасная конвертация строки в число с пл.запятой """
    try:
        result = float(text)
    except (ValueError, TypeError):
        result = 0.0
    return result


def calculate_effs(flws: list, lfts: list, pwrs: list):
    """ расчёт точек КПД """
    result = []
    count = len(flws)
    if count == len(lfts) and count == len(pwrs):
        result = [calculate_eff(flws[i], lfts[i], pwrs[i]) \
                for i in range(count)]
    return result


def calculate_eff(flw: float, lft: float, pwr: float):
    """ вычисление КПД """
    return 9.81 * lft * flw / (24 * 3600 * pwr) * 100 \
        if flw and lft and pwr else 0


def set_current_date(window):
    """ устанавливает текущую дату-время в соотв.поле """
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    window.txtDateTime.setText(today)


def process_mouse_wheel(obj, event, coef):
    """ обработка события колесика мыши на полях расход-напор-мощность """
    string = obj.text()
    val = float(string) if string else 0
    val += event.angleDelta().y() / 120 * coef
    val = round(val, 5)
    obj.setText(str(val if val >= 0 else 0))


def ask_password():
    """ проверка пароля """
    return Message.ask_password(
        'Внимание',
        'Необходимо подтверждение паролем:'
    ) == b'h\x87\x87\xd8\xff\x14LP,\x7f\\\xff\xaa\xfe,\xc5' \
         b'\x88\xd8`y\xf9\xde\x880L&\xb0\xcb\x99\xce\x91\xc6'
