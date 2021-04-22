def process_mouse_wheel(obj, event, coef):
    string = obj.text()
    val = float(string) if string else 0
    val += event.angleDelta().y() / 120 * coef
    obj.setText(str(val if val >= 0 else 0))
