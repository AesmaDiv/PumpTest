"""
    Модуль описывает структуру хранения информации об испытании
    и класс по управлению этой информацией
"""
from dataclasses import dataclass, field
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm.session import Session
from Classes.Data.alchemy_tables import Pump, Test
from Classes.Data.record import RecordType, RecordPump, RecordTest
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
        self._engine = create_engine(f'sqlite:///{path_to_db}')
        self._meta = MetaData(self._engine)
        self._testdata = TestData(self)

    def session(self):
        """ создаёт новую сессию для запросов """
        return Session(self._engine)

    def getTestdata(self):
        """ возвращает ссылку на информацию об записи """
        return self._testdata

    @Journal.logged
    def clearRecord(self):
        """ очищает информацию о записи """
        self.clearTypeInfo()
        self.clearPumpInfo()
        self.clearTestInfo()
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
            with self.session() as session:
                query = session.query(Test).where(Test.ID == test_id)
                if query.count():
                    session.delete(query.one())
                    session.commit()

    def clearTypeInfo(self):
        """ очистка информации о типоразмере """
        self._testdata.type_.clear()

    def clearPumpInfo(self):
        """ очистка информации о насосе """
        self._testdata.pump_.clear()

    def clearTestInfo(self):
        """ очистка информации о тесте """
        self._testdata.test_.clear()

    def getTestsList(self):
        """ получает список тестов """
        result = []
        with Session(self._engine) as session:
            result = session.query(
                Test.ID, Test.DateTime, Test.OrderNum, Pump.Serial
            ).filter(Test.Pump == Pump.ID).order_by(Test.ID.desc()).all()
        return list(map(dict, result))

    def getListFor(self, table_class, fields):
        """ получает список элементов из таблицы """
        result = []
        with Session(self._engine) as session:
            columns = [getattr(table_class, field) for field in fields]
            result = session.query(*columns).all()
        return list(map(dict, result))

    def checkExists_serial(self, serial, type_id=0):
        """ возвращает ID записи с введенным серийным номером """
        with Session(self._engine) as session:
            query = session.query(Pump).where(
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

    def checkExists_ordernum(self, order_num, with_select=False):
        """ возвращает ID записи с введенным номером наряд-заказа """
        with Session(self._engine) as session:
            query = session.query(Test).where(Test.OrderNum == order_num)
            if query.count():
                if with_select:
                    choice =  Message.choice(
                        "Внимание",
                        "Запись с таким наряд-заказом "
                        "уже присутствует в базе данных.\n"
                        "Хотите выбрать её или создать новую?",
                        ("Выбрать", "Создать", "Отмена")
                    )
                return query.one().ID, choice
        return 0, -1

    @Journal.logged
    def saveTestInfo(self):
        """ сохраняет информацию о тесте """
        self._testdata.test_['Pump'] = self._testdata.pump_['ID']
        self._testdata.test_.write()

    @Journal.logged
    def savePumpInfo(self) -> bool:
        """ сохраняет информацию о насосе """
        return self._testdata.pump_.write()
