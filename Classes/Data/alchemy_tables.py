"""
    Модуль классов связываемых с таблицами базы данных
"""
from ctypes.wintypes import DOUBLE
from dataclasses import dataclass
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import FLOAT, INTEGER, VARCHAR, String


Base = declarative_base()

@dataclass
class Connection(Base):
    """ Класс заказчика """
    __tablename__ = 'Connections'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Customer(Base):
    """ Класс заказчика """
    __tablename__ = 'Customers'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Group(Base):
    """ Класс заказчика """
    __tablename__ = 'Groups'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Material(Base):
    """ Класс заказчика """
    __tablename__ = 'Materials'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Size(Base):
    """ Класс сборки """
    __tablename__ = 'Sizes'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Owner(Base):
    """ Класс заказчика """
    __tablename__ = 'Owners'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Producer(Base):
    """ Класс производителя """
    __tablename__ = 'Producers'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Pump(Base):
    """ Класс насоса """
    __tablename__ = 'Pumps'
    ID = Column('ID', INTEGER, primary_key=True)
    Serial = Column('Serial', VARCHAR)
    Type = Column('Type', INTEGER, ForeignKey("Types.ID"))
    Group = Column('Group', INTEGER, ForeignKey("Groups.ID"))
    Material = Column('Material', INTEGER, ForeignKey("Materials.ID"))
    Size = Column('Size', INTEGER, ForeignKey("Sizes.ID"))
    Length = Column('Length', VARCHAR)
    Stages = Column('Stages', INTEGER)
    Connection = Column('Connection', INTEGER, ForeignKey("Connections.ID"))
    Test = relationship("Test")


@dataclass
class SectionStatus(Base):
    """ Класс сборки """
    __tablename__ = 'SectionStatuses'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class SectionType(Base):
    """ Класс сборки """
    __tablename__ = 'SectionTypes'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Efficiency(Base):
    """ Класс сборки """
    __tablename__ = 'Efficiencies'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)


@dataclass
class Test(Base):
    """ Класс испытания """
    __tablename__ = 'Tests'
    ID = Column('ID', INTEGER, primary_key=True)
    Pump = Column('Pump', INTEGER, ForeignKey("Pumps.ID"))
    DateTime = Column('DateTime', String)
    DateAssembled = Column('DateAssembled', String)
    Customer = Column('Customer', INTEGER, ForeignKey("Customers.ID"))
    Owner = Column('Owner', INTEGER, ForeignKey("Owners.ID"))
    OrderNum = Column('OrderNum', VARCHAR)
    Location = Column('Location', VARCHAR)
    Lease = Column('Lease', VARCHAR)
    Well = Column('Well', VARCHAR)
    DaysRun = Column('DaysRun', INTEGER)
    SectionStatus = Column('SectionStatus', INTEGER, ForeignKey("SectionStatuses.ID"))
    SectionType = Column('SectionType', INTEGER, ForeignKey("SectionTypes.ID"))
    SectionStatus = Column('SectionStatus', INTEGER, ForeignKey("SectionStatuses.ID"))
    ShaftDiameter = Column('ShaftDiameter', FLOAT)
    ShaftOut = Column('ShaftOut', FLOAT)
    ShaftIn = Column('ShaftIn', FLOAT)
    ShaftWobb = Column('ShaftWobb', FLOAT)
    ShaftMomentum = Column('ShaftMomentum', FLOAT)
    Flows = Column('Flows', VARCHAR)
    Lifts = Column('Lifts', VARCHAR)
    Powers = Column('Powers', VARCHAR)
    Comments = Column('Comments', VARCHAR)
    Vibrations = Column('Vibrations', VARCHAR)


@dataclass
class Type(Base):
    """ Класс типоразмера """
    __tablename__ = 'Types'
    ID = Column('ID', INTEGER, primary_key=True)
    Name = Column('Name', VARCHAR)
    Producer = Column('Producer', INTEGER, ForeignKey("Producers.ID"))
    Efficiency = Column('Efficiency', INTEGER, ForeignKey("Efficiencies.ID"))
    Date = Column('Date', VARCHAR)
    Rpm = Column('Rpm', FLOAT)
    Min = Column('Min', FLOAT)
    Nom = Column('Nom', FLOAT)
    Max = Column('Max', FLOAT)
    Flows = Column('Flows', VARCHAR)
    Lifts = Column('Lifts', VARCHAR)
    Powers = Column('Powers', VARCHAR)
