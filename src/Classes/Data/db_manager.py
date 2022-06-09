"""
    Модуль описывает структуру хранения информации об испытании
    и класс по управлению этой информацией
"""
from loguru import logger
from sqlalchemy import create_engine, MetaData, exc
from sqlalchemy.orm.session import sessionmaker

from Classes.Data.db_tables import Producer, Pump, Test, Type
from Classes.Data.record import Record


class DataManager:
    """Класс менеджера базы данных"""
    def __init__(self, path_to_db) -> None:
        self._path_to_db = path_to_db
        self._engine = create_engine(f'sqlite:///{path_to_db}')
        self._meta = MetaData(self._engine)

    def execute(self, func, *args, **kwargs):
        """выполнение запросов к БД и очистка"""
        # engine = create_engine(f'sqlite:///{self._path_to_db}')
        Session = sessionmaker(self._engine)
        with Session() as session:
            kwargs.update({'session': session})
            result = func(*args, **kwargs)
            session.close()
        # engine.dispose()
        return result

    def createRecord(self, data: dict) -> int:
        """создание новой записи"""
        logger.debug(f'{self.createRecord}')
        record = Record()
        for key, val in data.items():
            record[key] = val
        record.write()
        return record.ID

    def loadRecord(self, db_table, rec_id: int) -> dict:
        """загрузка информации о записи"""
        logger.debug(f'{self.loadRecord.__doc__} {db_table.__doc__} № {rec_id}')
        def func(**kwargs):
            query = kwargs['session'].query(
                db_table,
            ).where(
                db_table.ID == rec_id
            )
            return query.one() if query.count() else None
        result = self.execute(func)
        return DataManager._convertToDict(result)

    def loadRecord_Pump(self, rec_id) -> list:
        """загружаем полную информацию о насосе"""
        def func(**kwargs):
            query = kwargs['session'].query(
                Pump, Type, Producer
            ).where(
                Pump.ID == rec_id
            ).where(
                Type.ID == Pump.Type
            ).where(
                Producer.ID == Type.Producer
            )
            return query.one() if query.count() else None
        result = self.execute(func)
        return [DataManager._convertToDict(item) for item in result]

    def loadRecord_All(self, rec_id) -> list:
        """загружаем полную информацию о записи"""
        def func(**kwargs):
            query = kwargs['session'].query(
                Test, Pump, Type, Producer
            ).where(
                Test.ID == rec_id
            ).where(
                Pump.ID == Test.Pump
            ).where(
                Type.ID == Pump.Type
            ).where(
                Producer.ID == Type.Producer
            )
            return query.one() if query.count() else None
        result = self.execute(func)
        return [DataManager._convertToDict(item) for item in result]

    def removeRecord(self, db_table, rec_id):
        """удаляет текущую запись из БД"""
        session = sessionmaker(self._engine)
        with session() as session_:
            query = session_.query(db_table).where(db_table.ID == rec_id)
            if query.count():
                session_.delete(query.one())
                session_.commit()
            session_.close()
            self._engine.dispose()

    def writeRecord(self, db_table, data: dict) -> bool:
        """записывает данные в БД (data должен содержать ключ ID)"""
        def func(**kwargs):
            data_ = data.copy()
            id_ = data_.pop('ID')
            item = kwargs['session'].query(db_table).get(id_) if id_ else db_table()
            for k in data_.keys():
                setattr(item, k, data_[k])
            kwargs['session'].add(item)
            try:
                kwargs['session'].commit()
                data.update({'ID': item.ID })
            except exc.IntegrityError:
                return False
            return item.ID > 0
        return self.execute(func)

    def getTestsList(self) -> list:
        """получает список тестов"""
        def func(**kwargs):
            query = kwargs['session'].query(
                    Test.ID, Test.DateTime, Test.OrderNum, Pump.Serial
                ).filter(
                    Test.Pump == Pump.ID
                ).order_by(
                    Test.ID.desc()
                ).all()
            return query
        result = self.execute(func)
        return list(map(dict, result))

    def getListFor(self, table_class, fields) -> list:
        """получает список элементов из таблицы"""
        def func(**kwargs):
            columns = [getattr(table_class, field) for field in fields]
            result = kwargs['session'].query(*columns).all()
            return result
        result = self.execute(func)
        return list(map(dict, result))

    def findRecord_Type(self, type_name, producer_id):
        """возвращает запись с введенным именем типоразмера"""
        def func(**kwargs):
            query = kwargs['session'].query(
                Type
            ).where(
                Type.Name ==type_name
            ).filter(
                Type.Producer == producer_id
            )
            if query.count():
                return query.all()
            return None
        result = self.execute(func)
        return DataManager._convertToDict(result)

    def findRecord_Pump(self, serial, type_id) -> Record:
        """возвращает запись с введенным серийным номером"""
        def func(**kwargs):
            query = kwargs['session'].query(
                Pump
            ).where(
                Pump.Serial == serial
            ).filter(
                Pump.Type == type_id
            )
            if query.count():
                return query.one()
            return None
        result = self.execute(func)
        return DataManager._convertToDict(result)

    def findRecord_Test(self, order_num) -> Record:
        """возвращает запись с введенным номером наряд-заказа"""
        def func(**kwargs):
            query = kwargs['session'].query(
                Test
            ).where(
                Test.OrderNum == order_num
            )
            return query.one() if query.count() else None
        result = self.execute(func)
        return DataManager._convertToDict(result)

    @staticmethod
    def _convertToDict(record: Record) -> dict:
        try:
            return record.__dict__ if record else {}
        except AttributeError as err:
            logger.error(f"Error convering {record.__name__} to dictionary")
            logger.error(str(err))
            return {}
