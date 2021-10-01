from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm.session import Session
from Classes.Data.alchemy_tables import Assembly, Customer, Producer, Type, Pump, Test
from Classes.Data.record import RecordType, RecordPump, RecordTest
from AesmaLib.message import Message
from AesmaLib.journal import Journal


class TestData:
    """ Класс для полной информации об испытании """
    def __init__(self, db_manager) -> None:
        self.type_ = RecordType(db_manager)
        self.pump_ = RecordPump(db_manager)
        self.test_ = RecordTest(db_manager)
        self.dlts_ = {}


class DataManager:
    """ Класс менеджера базы данных """
    def __init__(self, path_to_db) -> None:
        self._engine = create_engine(f'sqlite:///{path_to_db}')
        self._meta = MetaData(self._engine)
        self._testdata = TestData(self)
        # self._assemblies = self._create_and_map_table(Assembly)
        # self._customers = self._create_and_map_table(Customer)
        # self._producers = self._create_and_map_table(Producer)
        # self._types = self._create_and_map_table(Type)
        # self._pumps = self._create_and_map_table(Pump)
        # self._tests = self._create_and_map_table(Test)

    def _create_and_map_table(self, cls):
        result = Table(cls.__tablename__, self._meta, autoload=True)
        # mapper(cls, result)
        return result

    def session(self):
        return Session(self._engine)

    def get_testdata(self):
        return self._testdata

    def clear_record(self):
        self.clear_type_info()
        self.clear_pump_info()
        self.clear_test_info()
        self._testdata.dlts_ = {}

    def clear_type_info(self):
        self._testdata.type_.clear()

    def clear_pump_info(self):
        self._testdata.pump_.clear()

    def clear_test_info(self):
        self._testdata.test_.clear()

    def get_tests_list(self):
        result = []
        with Session(self._engine) as session:
            result = session.query(
                Test.ID, Test.DateTime, Test.OrderNum, Pump.Serial
            ).filter(Test.Pump == Pump.ID).order_by(Test.ID.desc()).all()
        return list(map(dict, result))

    def get_list_for(self, table_class, fields):
        result = []
        with Session(self._engine) as session:
            columns = [getattr(table_class, field) for field in fields]
            result = session.query(*columns).all()
        return list(map(dict, result))


    def check_exists_serial(self, serial):
        """ возвращает ID записи с введенным номером наряд-заказа"""
        with Session(self._engine) as session:
            pump_id = session.query(Pump).where(Pump.Serial == serial).one()
            if pump_id:
                choice =  Message.ask(
                    "Внимание",
                    "Насос с таким заводским номером "
                    "уже присутствует в базе данных.\n"
                    "Хотите выбрать его?",
                    "Выбрать", "Отмена"
                )
                return pump_id['ID'], choice
        return 0, False

    def check_exists_ordernum(self, order_num, with_select=False):
        """ возвращает ID записи с введенным номером наряд-заказа"""
        with Session(self._engine) as session:
            test_id = session.query(Test).where(Test.OrderNum == order_num)
            if test_id:
                if with_select:
                    choice =  Message.choice(
                        "Внимание",
                        "Запись с таким наряд-заказом "
                        "уже присутствует в базе данных.\n"
                        "Хотите выбрать её или создать новую?",
                        ("Выбрать", "Создать", "Отмена")
                    )
                return test_id['ID'], choice
        return 0, -1

    @Journal.logged
    def save_test_info(self):
        """ сохраняет информацию о насосе """
        Journal.log(f"{__name__}::\t сохраняет информацию о новом тесте")
        self._testdata.test_['Pump'] = self._testdata.pump_['ID']
        self._testdata.test_.save()

    @Journal.logged
    def save_pump_info(self) -> bool:
        """ сохраняет информацию о насосе """
        return self._testdata.pump_.save()


    if __name__ == '__main__':
        import os
        path = os.path.join(os.path.dirname(__file__), '../Files/pump.sqlite')
        dbm = DataManager(path)
        retval = dbm.session().query(Test.ID, Test.DateTime, Pump.Serial).filter(Test.Pump == Pump.ID)
        for i in retval:
            dictionary = dict(i)
            # result['DateTime'] = f"{result['DateTime']:%Y-%m-%d %H:%M:%S}"
            print(dictionary)
