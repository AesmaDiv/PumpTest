from PyQt5.QtWidgets import QApplication, QGroupBox, QLineEdit, QComboBox, QPushButton, QWidget

from AesmaLib import Journal, AesmaFuncs
from AppClasses.Functions import funcsTable, funcsSpinner, funcsDB, funcsMessages
import vars


class Info:
    @staticmethod
    def clear(group: QGroupBox):
        widgets = group.findChildren(QWidget)
        for item in widgets:
            if isinstance(item, QLineEdit):
                item.clear()
            elif isinstance(item, QComboBox):
                item.setCurrentIndex(0)
        group.repaint()

    @staticmethod
    def set_readonly(group: QGroupBox, state: bool):
        widgets = group.findChildren(QWidget)
        for item in widgets:
            if isinstance(item, QLineEdit):
                item.setReadOnly(state)
            elif isinstance(item, QComboBox):
                item.setEnabled(not state)
            elif isinstance(item, QPushButton):
                if '_New' in item.objectName():
                    item.show() if state else item.hide()
                else:
                    item.hide() if state else item.show()
            if state:
                item.clearFocus()
        group.repaint()


class Test(Info):
    @staticmethod
    def load(test_id: int = 0):
        if test_id <= 0:
            data: dict = funcsTable.get_row(vars.wnd_main.tableTests)
            if data and 'ID' in data.keys():
                test_id: int = data['ID']
            else:
                return False
        vars.dictTest = funcsDB.get_record('Tests', conditions={'ID': test_id})

        return True

    @staticmethod
    def clear(group: QGroupBox):
        vars.dictTest.clear()
        Info.clear(group)

    @staticmethod
    def display():
        vars.wnd_main.txtDateTime.setText(vars.dictTest['DateTime'])
        vars.wnd_main.txtOrderNum.setText(vars.dictTest['OrderNum'])
        vars.wnd_main.txtLocation.setText(vars.dictTest['Location'])
        vars.wnd_main.txtLease.setText(vars.dictTest['Lease'])
        vars.wnd_main.txtWell.setText(vars.dictTest['Well'])
        vars.wnd_main.txtDaysRun.setText(str(vars.dictTest['DaysRun']))
        funcsSpinner.select_item_containing(vars.wnd_main.cmbCustomers, {'ID': vars.dictTest['Customer']})
        funcsSpinner.select_item_containing(vars.wnd_main.cmbAssembly, vars.dictTest['Assembly'])
        Test.fill_points_table()
        pass

    @staticmethod
    def fill_points_table():
        funcsTable.clear_table(vars.wnd_main.tablePoints)
        if vars.dictTest['Flows'] and vars.dictTest['Lifts'] and vars.dictTest['Powers']:
            points = [[val.strip() for val in vars.dictTest['Flows'].split(',')],
                      [val.strip() for val in vars.dictTest['Lifts'].split(',')],
                      [val.strip() for val in vars.dictTest['Powers'].split(',')]]
            for i in range(len(points[0])):
                funcsTable.add_row(vars.wnd_main.tablePoints,
                                   {'flow': points[0][i], 'lift': points[1][i], 'power': points[2][i]})

    @staticmethod
    def check_exist():
        test_id: int = 0
        order_num: str = vars.wnd_main.txtOrderNum.text()
        record = funcsDB.get_value('Tests', 'ID', {'OrderNum': order_num})
        if record is not None and len(record):
            test_id = record['ID']
        return test_id

    @staticmethod
    def check_all_filled():
        result: bool = True
        missing = []
        result &= check_value(vars.wnd_main.txtOrderNum.text(), 'Наряд-заказ\n', missing)
        result &= check_value(funcsSpinner.get_current_value(vars.wnd_main.cmbCustomers), 'Заказчик\n', missing)
        result &= check_value(funcsSpinner.get_current_value(vars.wnd_main.cmbAssembly), 'Сборка\n', missing)
        # result &= check_value(vars.wnd_main.txtLocation.text(), 'Месторождение\n', missing)
        # result &= check_value(vars.wnd_main.txtLease.text(), 'Куст\n', missing)
        # result &= check_value(vars.wnd_main.txtWell.text(), 'Скважина\n', missing)
        # result &= check_value(int(vars.wnd_main.txtDaysRun.text()), 'Суткопробег\n', missing)
        if not result:
            message = ''.join(missing)
            funcsMessages.show("Внимание", "Добавьте информацию о насосе:\n" + message)
        return result

    @staticmethod
    def save_to_vars_info():
        vars.dictTest['Pump'] = vars.dictPump['ID']
        vars.dictTest['DateTime'] = vars.wnd_main.txtDateTime.text()
        vars.dictTest['Customer'] = AesmaFuncs.safe_parse_to(int,
                                                             funcsSpinner.get_current_value(vars.wnd_main.cmbCustomers,
                                                                                            'ID'))
        vars.dictTest['Assembly'] = funcsSpinner.get_current_value(vars.wnd_main.cmbAssembly)
        vars.dictTest['OrderNum'] = vars.wnd_main.txtOrderNum.text()
        vars.dictTest['Location'] = vars.wnd_main.txtLocation.text()
        vars.dictTest['Lease'] = vars.wnd_main.txtLease.text()
        vars.dictTest['Well'] = vars.wnd_main.txtWell.text()
        vars.dictTest['DaysRun'] = vars.wnd_main.txtDaysRun.text()
        return True

    @staticmethod
    def save_to_db_info():
        return funcsDB.insert_record('Tests', vars.dictTest)

    @staticmethod
    def save_info():
        return Test.check_all_filled() and \
               Test.save_to_vars_info() and \
               Test.save_to_db_info()

    @staticmethod
    def save_to_vars_data():
        points = funcsTable.get_data(vars.wnd_main.tablePoints)
        points_data = AesmaFuncs.merge_dictionaries(points)
        vars.dictTest['Flows'] = ', '.join(map(str, points_data['flow']))
        vars.dictTest['Lifts'] = ', '.join(map(str, points_data['lift']))
        vars.dictTest['Powers'] = ', '.join(map(str, points_data['power']))
        return True

    @staticmethod
    def save_to_db_data():
        return funcsDB.update_record('Tests', vars.dictTest)

    @staticmethod
    def save_data():
        return Test.save_to_vars_data() and Test.save_to_db_data()


class Pump(Info):
    @staticmethod
    def load(pump_id: int = 0):
        if pump_id <= 0:
            pump_id = vars.dictTest['Pump'] if vars.dictTest else 0
            if not pump_id:
                return False
        vars.dictPump = funcsDB.get_record('Pumps', conditions={'ID': pump_id})
        type_id: int = vars.dictPump['Type']
        Type.load(type_id)
        return True

    @staticmethod
    def clear(group: QGroupBox):
        vars.dictPump.clear()
        vars.dictType.clear()
        Info.clear(group)

    @staticmethod
    def display():
        funcsSpinner.select_item_containing(vars.wnd_main.cmbProducers, {'ID': vars.dictType['Producer']})
        funcsSpinner.select_item_containing(vars.wnd_main.cmbTypes, {'ID':  vars.dictPump['Type']})
        funcsSpinner.select_item_containing(vars.wnd_main.cmbSerials, {'Serial': vars.dictPump['Serial']})
        vars.wnd_main.txtLength.setText(vars.dictPump['Length'])
        vars.wnd_main.txtStages.setText(str(vars.dictPump['Stages']))
        vars.wnd_main.txtShaft.setText(vars.dictPump['Shaft'])
        vars.wnd_main.groupPumpInfo.repaint()
        pass

    @staticmethod
    def check_exist():
        pump_id: int = 0
        serial = funcsSpinner.get_current_value(vars.wnd_main.cmbSerials)
        record = funcsDB.get_value('Pumps', 'ID', {'Serial': serial})
        if record is not None and len(record):
            pump_id = record['ID']
        return pump_id

    @staticmethod
    def check_all_filled():
        result: bool = True
        missing = []
        result &= check_value(funcsSpinner.get_current_value(vars.wnd_main.cmbProducers), 'Производитель\n', missing)
        result &= check_value(funcsSpinner.get_current_value(vars.wnd_main.cmbTypes), 'Типоразмер\n', missing)
        result &= check_value(funcsSpinner.get_current_value(vars.wnd_main.cmbSerials), 'Заводской номер\n', missing)
        result &= check_value(vars.wnd_main.txtLength.text(), 'Длина\n', missing)
        result &= check_value(vars.wnd_main.txtStages.text(), 'Кол-во ступеней\n', missing)
        # result &= check_value(vars.wnd_main.txtShaft.text(), 'Вылет вала\n', missing)
        if not result:
            message = ''.join(missing)
            funcsMessages.show("Внимание", "Добавьте информацию о насосе:\n" + message)
        return result

    @staticmethod
    def save_to_vars():
        vars.dictPump['Type'] = AesmaFuncs.safe_parse_to(int, funcsSpinner.get_current_value(vars.wnd_main.cmbTypes, 'ID'))
        vars.dictPump['Serial'] = str(funcsSpinner.get_current_value(vars.wnd_main.cmbSerials))
        vars.dictPump['Length'] = vars.wnd_main.txtLength.text()
        vars.dictPump['Stages'] = AesmaFuncs.safe_parse_to(int, vars.wnd_main.txtStages.text())
        vars.dictPump['Shaft'] = vars.wnd_main.txtShaft.text()
        # vars.pump_type['Producer'] = int(funcsSpinner.get_current_value(vars.wnd_main.cmbProducers, 'ID'))
        return True

    @staticmethod
    def save_to_db():
        return funcsDB.insert_record('Pumps', vars.dictPump)

    @staticmethod
    def save():
        return Pump.check_all_filled() and Pump.save_to_vars() and Pump.save_to_db()


class Type:
    @staticmethod
    def load(type_id: int = 0):
        if type_id <= 0:
            type_id = vars.dictPump['Type'] if vars.dictPump else 0
            if not type_id:
                return False
        vars.dictType = funcsDB.get_record('Types', conditions={'ID': type_id})
        return True

    @staticmethod
    def clear(group: QGroupBox):
        vars.dictType.clear()
        Info.clear(group)

    @staticmethod
    def display():
        # vars.wnd_main.txtType_Date.setText(vars.pump_type['Date'])
        # vars.wnd_main.txtType_Rpm.setText(str(vars.pump_type['Rpm']))
        # vars.wnd_main.txtType_Min.setText(str(vars.pump_type['Min']))
        # vars.wnd_main.txtType_Nom.setText(str(vars.pump_type['Nom']))
        # vars.wnd_main.txtType_Max.setText(str(vars.pump_type['Max']))
        pass

    @staticmethod
    def clear():
        # vars.wnd_main.txtType_Date.clear()
        # vars.wnd_main.txtType_Rpm.clear()
        # vars.wnd_main.txtType_Min.clear()
        # vars.wnd_main.txtType_Nom.clear()
        # vars.wnd_main.txtType_Max.clear()
        pass

    @staticmethod
    def check_exist():
        type_id: int = 0
        text: str = funcsSpinner.get_current_value(vars.wnd_main.cmbTypes)
        record = funcsDB.get_value('Types', 'ID', {'Name': text})
        if record is not None and len(record):
            type_id = record['ID']
        return type_id

    @staticmethod
    def store():
        # try:
        #     vars.pump_type['Date'] = vars.wnd_main.txtTypeDate.toPlainText()
        #     vars.pump_type['Rpm'] = int(vars.wnd_main.txtTypeRpm.toPlainText())
        #     vars.pump_type['Min'] = int(vars.wnd_main.txtTypeMin.toPlainText())
        #     vars.pump_type['Nom'] = int(vars.wnd_main.txtTypeNom.toPlainText())
        #     vars.pump_type['Max'] = int(vars.wnd_main.txtTypeMax.toPlainText())
        #     return True
        # except BaseException as error:
        #     Journal.log(__name__ + " error: " + str(error))
        #     return False
        pass


def check_value(value, add_text: str, missing: list):
    if value is None or value == '':
        missing.append('    ' + add_text)
        return False
    return True
