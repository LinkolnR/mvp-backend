# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Tabela de comidas
class Food(Base):
    __tablename__ = "foods"
    food_id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, unique=True, index=True)
    price = Column(Float)
    co2_emission = Column(Float)
    image = Column(String)

    # Relacionamento com Transaction
    transactions = relationship("Transaction", back_populates="food")

# Tabela de motivos
class Reason(Base):
    __tablename__ = "reasons"
    reason_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relacionamento com Transaction
    transactions = relationship("Transaction", back_populates="reason")

# Tabela de transações
class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("foods.food_id"))
    reason_id = Column(Integer, ForeignKey("reasons.reason_id"))
    weight = Column(Float)
    date = Column(DateTime, default=datetime.now())
    

    # Relacionamento com Food e Reason
    food = relationship("Food", back_populates="transactions")
    reason = relationship("Reason", back_populates="transactions")

