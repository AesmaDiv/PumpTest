from PyQt5.QtWidgets import QApplication, QGroupBox, QComboBox
from PyQt5.QtWidgets import QLineEdit, QPushButton, QWidget

from AesmaLib import aesma_funcs
from AesmaLib.journal import Journal
from Functions import funcsTable, funcsSpinner, funcs_db, funcsMessages
from Globals import gvars


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
            data: dict = funcsTable.get_row(gvars.wnd_main.tableTests)
            if data and 'ID' in data.keys():
                test_id: int = data['ID']
            else:
                return False
        gvars.dictTest = funcs_db.get_record('Tests', conditions={'ID': test_id})

        return True

    @staticmethod
    def clear(group: QGroupBox):
        gvars.dictTest.clear()
        Info.clear(group)

    @staticmethod
    def display():
        gvars.wnd_main.txtDateTime.setText(gvars.dictTest['DateTime'])
        gvars.wnd_main.txtOrderNum.setText(gvars.dictTest['OrderNum'])
        gvars.wnd_main.txtLocation.setText(gvars.dictTest['Location'])
        gvars.wnd_main.txtLease.setText(gvars.dictTest['Lease'])
        gvars.wnd_main.txtWell.setText(gvars.dictTest['Well'])
        gvars.wnd_main.txtDaysRun.setText(str(gvars.dictTest['DaysRun']))
        funcsSpinner.select_item_containing(gvars.wnd_main.cmbCustomers, {'ID': gvars.dictTest['Customer']})
        funcsSpinner.select_item_containing(gvars.wnd_main.cmbAssembly, gvars.dictTest['Assembly'])
        Test.fill_points_table()
        pass

    @staticmethod
    def fill_points_table():
        funcsTable.clear_table(gvars.wnd_main.tablePoints)
        if gvars.dictTest['Flows'] and gvars.dictTest['Lifts'] and gvars.dictTest['Powers']:
            points = [[val.strip() for val in gvars.dictTest['Flows'].split(',')],
                      [val.strip() for val in gvars.dictTest['Lifts'].split(',')],
                      [val.strip() for val in gvars.dictTest['Powers'].split(',')]]
            for i in range(len(points[0])):
                funcsTable.add_row(gvars.wnd_main.tablePoints,
                                   {'flow': points[0][i], 'lift': points[1][i], 'power': points[2][i]})

    @staticmethod
    def check_exist():
        test_id: int = 0
        order_num: str = gvars.wnd_main.txtOrderNum.text()
        record = funcs_db.get_value('Tests', 'ID', {'OrderNum': order_num})
        if record is not None and len(record):
            test_id = record['ID']
        return test_id

    @staticmethod
    def check_all_filled():
        result: bool = True
        missing = []
        result &= check_value(gvars.wnd_main.txtOrderNum.text(), 'Наряд-заказ\n', missing)
        result &= check_value(funcsSpinner.get_current_value(gvars.wnd_main.cmbCustomers), 'Заказчик\n', missing)
        result &= check_value(funcsSpinner.get_current_value(gvars.wnd_main.cmbAssembly), 'Сборка\n', missing)
        # result &= check_value(gvars.wnd_main.txtLocation.text(), 'Месторождение\n', missing)
        # result &= check_value(gvars.wnd_main.txtLease.text(), 'Куст\n', missing)
        # result &= check_value(gvars.wnd_main.txtWell.text(), 'Скважина\n', missing)
        # result &= check_value(int(gvars.wnd_main.txtDaysRun.text()), 'Суткопробег\n', missing)
        if not result:
            message = ''.join(missing)
            funcsMessages.show("Внимание", "Добавьте информацию о насосе:\n" + message)
        return result

    @staticmethod
    def save_to_gvars_info():
        gvars.dictTest['Pump'] = gvars.dictPump['ID']
        gvars.dictTest['DateTime'] = gvars.wnd_main.txtDateTime.text()
        gvars.dictTest['Customer'] = aesma_funcs.safe_parse_to(int,
                                                             funcsSpinner.get_current_value(gvars.wnd_main.cmbCustomers,
                                                                                            'ID'))
        gvars.dictTest['Assembly'] = funcsSpinner.get_current_value(gvars.wnd_main.cmbAssembly)
        gvars.dictTest['OrderNum'] = gvars.wnd_main.txtOrderNum.text()
        gvars.dictTest['Location'] = gvars.wnd_main.txtLocation.text()
        gvars.dictTest['Lease'] = gvars.wnd_main.txtLease.text()
        gvars.dictTest['Well'] = gvars.wnd_main.txtWell.text()
        gvars.dictTest['DaysRun'] = gvars.wnd_main.txtDaysRun.text()
        return True

    @staticmethod
    def save_to_db_info():
        return funcs_db.insert_record('Tests', gvars.dictTest)

    @staticmethod
    def save_info():
        return Test.check_all_filled() and \
               Test.save_to_gvars_info() and \
               Test.save_to_db_info()

    @staticmethod
    def save_to_gvars_data():
        points = funcsTable.get_data(gvars.wnd_main.tablePoints)
        points_data = aesma_funcs.combine_dicts(points)
        gvars.dictTest['Flows'] = ', '.join(map(str, points_data['flow']))
        gvars.dictTest['Lifts'] = ', '.join(map(str, points_data['lift']))
        gvars.dictTest['Powers'] = ', '.join(map(str, points_data['power']))
        return True

    @staticmethod
    def save_to_db_data():
        return funcs_db.update_record('Tests', gvars.dictTest)

    @staticmethod
    def save_data():
        return Test.save_to_gvars_data() and Test.save_to_db_data()


class Pump(Info):
    @staticmethod
    def load(pump_id: int = 0):
        if pump_id <= 0:
            pump_id = gvars.dictTest['Pump'] if gvars.dictTest else 0
            if not pump_id:
                return False
        gvars.dictPump = funcs_db.get_record('Pumps', conditions={'ID': pump_id})
        type_id: int = gvars.dictPump['Type']
        Type.load(type_id)
        return True

    @staticmethod
    def clear(group: QGroupBox):
        gvars.dictPump.clear()
        gvars.dictType.clear()
        Info.clear(group)

    @staticmethod
    def display():
        funcsSpinner.select_item_containing(gvars.wnd_main.cmbProducers, {'ID': gvars.dictType['Producer']})
        funcsSpinner.select_item_containing(gvars.wnd_main.cmbTypes, {'ID':  gvars.dictPump['Type']})
        funcsSpinner.select_item_containing(gvars.wnd_main.cmbSerials, {'Serial': gvars.dictPump['Serial']})
        gvars.wnd_main.txtLength.setText(gvars.dictPump['Length'])
        gvars.wnd_main.txtStages.setText(str(gvars.dictPump['Stages']))
        gvars.wnd_main.txtShaft.setText(gvars.dictPump['Shaft'])
        gvars.wnd_main.groupPumpInfo.repaint()
        pass

    @staticmethod
    def check_exist():
        pump_id: int = 0
        serial = funcsSpinner.get_current_value(gvars.wnd_main.cmbSerials)
        record = funcs_db.get_value('Pumps', 'ID', {'Serial': serial})
        if record is not None and len(record):
            pump_id = record['ID']
        return pump_id

    @staticmethod
    def check_all_filled():
        result: bool = True
        missing = []
        result &= check_value(funcsSpinner.get_current_value(gvars.wnd_main.cmbProducers), 'Производитель\n', missing)
        result &= check_value(funcsSpinner.get_current_value(gvars.wnd_main.cmbTypes), 'Типоразмер\n', missing)
        result &= check_value(funcsSpinner.get_current_value(gvars.wnd_main.cmbSerials), 'Заводской номер\n', missing)
        result &= check_value(gvars.wnd_main.txtLength.text(), 'Длина\n', missing)
        result &= check_value(gvars.wnd_main.txtStages.text(), 'Кол-во ступеней\n', missing)
        # result &= check_value(gvars.wnd_main.txtShaft.text(), 'Вылет вала\n', missing)
        if not result:
            message = ''.join(missing)
            funcsMessages.show("Внимание", "Добавьте информацию о насосе:\n" + message)
        return result

    @staticmethod
    def save_to_gvars():
        gvars.dictPump['Type'] = aesma_funcs.safe_parse_to(int, funcsSpinner.get_current_value(gvars.wnd_main.cmbTypes, 'ID'))
        gvars.dictPump['Serial'] = str(funcsSpinner.get_current_value(gvars.wnd_main.cmbSerials))
        gvars.dictPump['Length'] = gvars.wnd_main.txtLength.text()
        gvars.dictPump['Stages'] = aesma_funcs.safe_parse_to(int, gvars.wnd_main.txtStages.text())
        gvars.dictPump['Shaft'] = gvars.wnd_main.txtShaft.text()
        # gvars.pump_type['Producer'] = int(funcsSpinner.get_current_value(gvars.wnd_main.cmbProducers, 'ID'))
        return True

    @staticmethod
    def save_to_db():
        return funcs_db.insert_record('Pumps', gvars.dictPump)

    @staticmethod
    def save():
        return Pump.check_all_filled() and Pump.save_to_gvars() and Pump.save_to_db()


class Type:
    @staticmethod
    def load(type_id: int = 0):
        if type_id <= 0:
            type_id = gvars.dictPump['Type'] if gvars.dictPump else 0
            if not type_id:
                return False
        gvars.dictType = funcs_db.get_record('Types', conditions={'ID': type_id})
        return True

    @staticmethod
    def clear(group: QGroupBox):
        gvars.dictType.clear()
        Info.clear(group)

    @staticmethod
    def display():
        # gvars.wnd_main.txtType_Date.setText(gvars.pump_type['Date'])
        # gvars.wnd_main.txtType_Rpm.setText(str(gvars.pump_type['Rpm']))
        # gvars.wnd_main.txtType_Min.setText(str(gvars.pump_type['Min']))
        # gvars.wnd_main.txtType_Nom.setText(str(gvars.pump_type['Nom']))
        # gvars.wnd_main.txtType_Max.setText(str(gvars.pump_type['Max']))
        pass

    @staticmethod
    def clear():
        # gvars.wnd_main.txtType_Date.clear()
        # gvars.wnd_main.txtType_Rpm.clear()
        # gvars.wnd_main.txtType_Min.clear()
        # gvars.wnd_main.txtType_Nom.clear()
        # gvars.wnd_main.txtType_Max.clear()
        pass

    @staticmethod
    def check_exist():
        type_id: int = 0
        text: str = funcsSpinner.get_current_value(gvars.wnd_main.cmbTypes)
        record = funcs_db.get_value('Types', 'ID', {'Name': text})
        if record is not None and len(record):
            type_id = record['ID']
        return type_id

    @staticmethod
    def store():
        # try:
        #     gvars.pump_type['Date'] = gvars.wnd_main.txtTypeDate.toPlainText()
        #     gvars.pump_type['Rpm'] = int(gvars.wnd_main.txtTypeRpm.toPlainText())
        #     gvars.pump_type['Min'] = int(gvars.wnd_main.txtTypeMin.toPlainText())
        #     gvars.pump_type['Nom'] = int(gvars.wnd_main.txtTypeNom.toPlainText())
        #     gvars.pump_type['Max'] = int(gvars.wnd_main.txtTypeMax.toPlainText())
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
