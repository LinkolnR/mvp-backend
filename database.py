

# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuração da URL do banco de dados (usando SQLite)
DATABASE_URL = "sqlite:///./food_data.db"

# Criação do engine e configuração da sessão
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# Função para obter uma sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
from sqlalchemy.orm import Session
from models import Food, Reason


def initialize_data(db: Session):
    # Verifica se há registros na tabela Food
    if db.query(Food).count() == 0:
        # Dados iniciais para a tabela Food
        initial_foods = [
            Food(food_id=1, food_name="Frango", price=20.00, image="frango.jpg", co2_emission=6.5),
            Food(food_id=2, food_name="Carne", price=35.00, image="carne.jpg", co2_emission=60.0),
            Food(food_id=3, food_name="Arroz", price=7.00, image="arroz.jpg", co2_emission=2.5),
        ]
        db.add_all(initial_foods)
        db.commit()
        print("Dados iniciais de Food adicionados.")

    # Verifica se há registros na tabela Reason
    if db.query(Reason).count() == 0:
        # Dados iniciais para a tabela Reason
        initial_reasons = [
            Reason(reason_id=1, name="Validade"),
            Reason(reason_id=2, name="Sobra"),
            Reason(reason_id=3, name="Resto"),
        ]
        db.add_all(initial_reasons)
        db.commit()
        print("Dados iniciais de Reason adicionados.")