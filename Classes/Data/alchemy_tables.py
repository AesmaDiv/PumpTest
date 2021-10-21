"""
    Модуль классов связываемых с таблицами базы данных
"""
from dataclasses import dataclass
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import FLOAT, INTEGER, VARCHAR, String


Base = declarative_base()
@dataclass
class Assembly(Base):
    """ Класс сборки """
    __tablename__ = 'Assemblies'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Customer(Base):
    """ Класс заказчика """
    __tablename__ = 'Customers'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Producer(Base):
    """ Класс производителя """
    __tablename__ = 'Producers'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Type(Base):
    """ Класс типоразмера """
    __tablename__ = 'Types'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)
    Producer = Column('Producer', INTEGER, ForeignKey("Producers.ID"))
    Date = Column('Date', VARCHAR)
    Rpm = Column('Rpm', FLOAT)
    Min = Column('Min', FLOAT)
    Nom = Column('Nom', FLOAT)
    Max = Column('Max', FLOAT)
    Flows = Column('Flows', VARCHAR)
    Lifts = Column('Lifts', VARCHAR)
    Powers = Column('Powers', VARCHAR)


@dataclass
class Pump(Base):
    """ Класс насоса """
    __tablename__ = 'Pumps'
    ID = Column('ID', INTEGER, primary_key=True)
    Serial = Column('Serial', VARCHAR)
    Type = Column('Type', INTEGER, ForeignKey("Types.ID"))
    Length = Column('Length', VARCHAR)
    Stages = Column('Stages', INTEGER)
    Shaft = Column('Shaft', VARCHAR)
    Test = relationship("Test")


@dataclass
class Test(Base):
    """ Класс испытания """
    __tablename__ = 'Tests'
    ID = Column('ID', INTEGER, primary_key=True)
    Pump = Column('Pump', INTEGER, ForeignKey("Pumps.ID"))
    DateTime = Column('DateTime', String)
    Customer = Column('Customer', INTEGER, ForeignKey("Customers.ID"))
    OrderNum = Column('OrderNum', VARCHAR)
    Assembly = Column('Assembly', INTEGER, ForeignKey("Assemblies.ID"))
    Location = Column('Location', VARCHAR)
    Lease = Column('Lease', VARCHAR)
    Well = Column('Well', VARCHAR)
    DaysRun = Column('DaysRun', INTEGER)
    Flows = Column('Flows', VARCHAR)
    Lifts = Column('Lifts', VARCHAR)
    Powers = Column('Powers', VARCHAR)
    Comments = Column('Comments', VARCHAR)
    Vibrations = Column('Vibrations', VARCHAR)
