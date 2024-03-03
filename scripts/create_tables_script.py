from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class OrdersTable(Base):
    __tablename__ = 'orders_table'

    InvoiceNo = Column(String(255), primary_key=True)
    InvoiceDate = Column(DateTime)
    CustomerID = Column(Integer, ForeignKey('customers_table.CustomerID'))
    StockCode = Column(String(255), ForeignKey('stock_table.StockCode'))
    Quantity = Column(Integer)

    stock = relationship('StockTable', backref='orders')
    customer = relationship('CustomersTable', backref='orders')

class CustomersTable(Base):
    __tablename__ = 'customers_table'

    CustomerID = Column(Integer, primary_key=True)
    Country = Column(String(255))


class StockTable(Base):
    __tablename__ = 'stock_table'

    StockCode = Column(String(255), primary_key=True)
    Description = Column(String(255))
    UnitPrice = Column(Float)


def create_tables_main(db_url):

    #create engine
    engine = create_engine(db_url)

    Base.metadata.create_all(engine)

    print("Tables created successfully!")

