"""
    Модуль описывает структуру хранения информации об испытании
    и класс по управлению этой информацией
"""
from dataclasses import dataclass, field
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm.session import sessionmaker
from Classes.Data.alchemy_tables import Pump, Test
from Classes.Data.record import Record, RecordType, RecordPump, RecordTest
from AesmaLib.message import Message
from AesmaLib.journal import Journal


@dataclass
class TestData:
    """ Класс для полной информации об записи """
    def __init__(self, db_manager) -> None:
        self.type_ = RecordType(db_manager)
        self.pump_ = RecordPump(db_manager)
        self.test_ = RecordTest(db_manager)
        self.dlts_ = field(default_factory=dict)


class DataManager:
    """ Класс менеджера базы данных """
    def __init__(self, path_to_db) -> None:
        self._path_to_db = path_to_db
        self._engine = create_engine(f'sqlite:///{path_to_db}')
        self._meta = MetaData(self._engine)
        self._testdata = TestData(self)

    def execute(self, func, *args, **kwargs):
        """ выполнение запросов к БД и очистка """
        engine = create_engine(f'sqlite:///{self._path_to_db}')
        Session = sessionmaker(engine)
        with Session() as session:
            kwargs.update({'session': session})
            result = func(*args, **kwargs)
            session.close()
        engine.dispose()
        return result

    @property
    def testdata(self):
        """ возвращает ссылку на информацию об записи """
        return self._testdata

    def createRecord(self, table_class, data: dict):
        """ создать новую запись """
        record = Record(self, table_class)
        for key, val in data.items():
            record[key] = val
        record.write()
        return record.ID

    @Journal.logged
    def clearRecord(self):
        """ очищает информацию о записи """
        self.clearInfo_Type()
        self.clearInfo_Pump()
        self.clearInfo_Test()
        self._testdata.dlts_ = {}

    def loadRecord(self, test_id: int) -> bool:
        """ загружает информацию о тесте """
        Journal.log_func(self.loadRecord, test_id)
        return self._testdata.test_.read(test_id)

    @Journal.logged
    def removeCurrentRecord(self):
        """ удаляет текущую запись из БД"""
        test_id = self._testdata.test_['ID']
        if test_id:
            session = sessionmaker(self._engine)
            with session() as session_:
                query = session_.query(Test).where(Test.ID == test_id)
                if query.count():
                    session_.delete(query.one())
                    session_.commit()
                session_.close()
                self._engine.dispose()

    def clearInfo_Type(self):
        """ очистка информации о типоразмере """
        self._testdata.type_.clear()

    def clearInfo_Pump(self):
        """ очистка информации о насосе """
        self._testdata.pump_.clear()

    def clearInfo_Test(self):
        """ очистка информации о тесте """
        self._testdata.test_.clear()

    def getTestsList(self):
        """ получает список тестов """
        def func(**kwargs):
            session_ = kwargs['session']
            result = session_.query(
                    Test.ID, Test.DateTime, Test.OrderNum, Pump.Serial
                ).filter(Test.Pump == Pump.ID).order_by(Test.ID.desc()).all()
            return result
        result = self.execute(func)
        return list(map(dict, result))

    def getListFor(self, table_class, fields):
        """ получает список элементов из таблицы """
        def func(**kwargs):
            columns = [getattr(table_class, field) for field in fields]
            result = kwargs['session'].query(*columns).all()
            return result
        result = self.execute(func)
        return list(map(dict, result))

    def checkExists_Serial(self, serial, type_id=0):
        """ возвращает ID записи с введенным серийным номером """
        def func(**kwargs):
            query = kwargs['session'].query(Pump).where(
                Pump.Serial == serial
            ).filter(Pump.Type == type_id)
            if query.count():
                choice =  Message.ask(
                    "Внимание",
                    "Насос с таким заводским номером "
                    "уже присутствует в базе данных.\n"
                    "Хотите выбрать его?",
                    "Выбрать", "Отмена"
                )
                return query.one().ID, choice
            return 0, False
        result_id, result_state = self.execute(func)
        return result_id, result_state

    def checkExists_OrderNum(self, order_num):
        """ возвращает ID записи с введенным номером наряд-заказа """
        def func(**kwargs):
            query = kwargs['session'].query(Test).where(Test.OrderNum == order_num)
            if query.count():
                choice =  Message.ask(
                    "Внимание",
                    "Запись с таким наряд-заказом "
                    "уже присутствует в базе данных.\n"
                    "Хотите выбрать её или создать новую?",
                    "Выбрать", "Отмена"
                )
                return query.one().ID, choice
            return 0, False
        return self.execute(func)

    def findRecord_Ordernum(self, order_num):
        """ поиск записи по номеру наряд-заказа """
        def func(**kwargs):
            query = kwargs['session'].query(Test).where(
                Test.OrderNum == order_num
            )
            return query.one().ID if query.count() else 0
        return self.execute(func)

    @Journal.logged
    def saveInfo_Pump(self) -> bool:
        """ сохраняет информацию о насосе """
        return self._testdata.pump_.write()

    @Journal.logged
    def saveInfo_Test(self) -> bool:
        """ сохраняет информацию о тесте """
        self._testdata.test_['Pump'] = self._testdata.pump_['ID']
        return self._testdata.test_.write()
