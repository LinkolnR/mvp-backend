# main.py
from http.client import HTTPException
from fastapi import FastAPI, WebSocket, Depends, Query, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine, get_db, initialize_data
from models import Base, Food, Reason, Transaction
from datetime import datetime
import threading
import serial
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


# Configurações de serial
porta_serial = 'COM9'
baudrate = 9600
bits_de_dados = 8
paridade = serial.PARITY_NONE
bits_de_parada = serial.STOPBITS_ONE
tamanho_leitura = 7

ultimo_dado_balança = None
executando = True

# Inicializa a aplicação
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa os templates do Jinja2
templates = Jinja2Templates(directory="templates")
# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicializa dados para tabelas Food e Reason
db = next(get_db())  # Corrigido para utilizar next() em vez de with
initialize_data(db)  # Chama a função de inicialização dos dados

# Modelo Pydantic para dados de alimentos
class FoodItem(BaseModel):
    foodId: int
    foodPrice: float
    motivoId: int


# Gerencia a conexão WebSocket e atualizações
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

# Rota WebSocket para atualizações em tempo real
@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Recebe mensagens dos clientes (se necessário)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Função para processar e salvar as leituras de alimentos
@app.post("/submit")
async def submit_form(food_item: FoodItem, db: Session = Depends(get_db)):
    print(food_item)
    food_id = food_item.foodId
    food_price = food_item.foodPrice
    motivo_id = food_item.motivoId

    # Verifica se o dado da balança foi recebido corretamente
    if ultimo_dado_balança:
        reading = int(ultimo_dado_balança) / 100
    else:
        reading = 10.00

    # Verifica se o item de comida já existe, senão cria um novo
    food = db.query(Food).filter(Food.food_id == food_id).first()
    if not food:
        food = Food(food_id=food_id, food_name=food_name, price=food_price)
        db.add(food)
        db.commit()
        db.refresh(food)
    
    # Verifica se o motivo já existe
    reason = db.query(Reason).filter(Reason.reason_id == motivo_id).first()
    if not reason:
        return JSONResponse(
            content={"message": "Motivo não encontrado."},
            status_code=400
        )

    # Cria uma nova transação (leitura) com o motivo associado
    new_reading = Transaction(
        food_id=food.food_id,
        reason_id=reason.reason_id,
        weight=reading,
        date=datetime.utcnow(),
    )
    db.add(new_reading)
    db.commit()

    # Envia dados de atualização via WebSocket
    await manager.broadcast(f"New reading: {reading}")
    return JSONResponse(content={"message": "Registro criado com sucesso"})


# Função para obter dados de resumo
@app.get("/food-waste/summary")
async def get_summary(db: Session = Depends(get_db)):
    total_weight = db.query(func.sum(Transaction.weight)).scalar() or 0
    total_value = db.query(func.sum(Transaction.weight * Food.price)).join(Food).scalar() or 0
    total_transactions = db.query(Transaction).count()
    return JSONResponse(content={
        "total_weight": total_weight,
        "total_value": total_value,
        "total_transactions": total_transactions
    })


from sqlalchemy.sql import func
from fastapi.responses import JSONResponse

# Função para obter dados para gráficos com total de custo incluído, agrupado por name e food_name
@app.get("/food-waste/graph-data")
async def get_graph_data(db: Session = Depends(get_db)):
    # Realiza a consulta para obter o nome do alimento, nome do motivo e custo total para cada grupo
    results = (
        db.query(
            Food.food_name,
            Reason.name,  # Usa "name" como nome do motivo e o renomeia para "reason_name"
            func.sum(Transaction.weight * Food.price).label("total_cost")
        )
        .select_from(Transaction)  # Define o ponto de partida da consulta
        .join(Food, Food.food_id == Transaction.food_id)  # Faz o join explícito com Food
        .join(Reason, Reason.reason_id == Transaction.reason_id)  # Faz o join explícito com Reason
        .group_by(Food.food_name, Reason.name)  # Agrupa por food_name e name
        .order_by(func.sum(Transaction.weight * Food.price).desc())  # Ordena pelo custo total em ordem decrescente
        .all()
    )

    # Prepara os dados para retornar como JSON
    graph_data = [
        {"food_name": result.food_name, "label": result.name, "total_cost": result.total_cost}
        for result in results
    ]

    # Retorna o JSON com a estrutura solicitada
    return JSONResponse(content={"data": graph_data})

# Função para obter dados para gráficos com total de custo incluído, agrupado por name e food_name
@app.get("/food-waste/co2_emission")
async def get_top_co2_emitting_foods(db: Session = Depends(get_db)):
    try:
        # Realiza a consulta para obter o nome do alimento e a soma de CO₂ emitido
        results = (
            db.query(
                Food.food_name,
                func.sum(Food.co2_emission).label("total_co2_emission")
            )
            .join(Transaction, Food.food_id == Transaction.food_id)
            .group_by(Food.food_name)
            .order_by(func.sum(Food.co2_emission).desc())  # Ordena pela soma de CO₂ em ordem decrescente
            .limit(5)  # Limita para os 5 alimentos com maior emissão de CO₂
            .all()
        )

        # Prepara os dados para retornar como JSON
        co2_data = [
            {"food_name": result.food_name, "total_co2_emission": result.total_co2_emission}
            for result in results
        ]
        print(co2_data)
        # Retorna o JSON com a estrutura solicitada
        return JSONResponse(content={"data": co2_data})
    
    except Exception as e:
        print("Error fetching CO₂ emissions data:", e)
        raise HTTPException(status_code=500, detail="Error fetching CO₂ emissions data")






@app.get("/food-waste/reasons")
async def get_reasons(db: Session = Depends(get_db)):

    lista_de_motivos = db.query(Reason).all()
    lista_de_motivos = [motivo.__dict__ for motivo in lista_de_motivos]
    
    for motivo in lista_de_motivos:
        motivo.pop('_sa_instance_state')
    # faca um dicionario para mandar de nome : id
    dict_motivos = {motivo['name']: motivo['reason_id'] for motivo in lista_de_motivos}


    return JSONResponse(content={
        "reasons": dict_motivos
    })

@app.get("/food-waste/filter-by-date-and-reason")
async def filter_by_date_and_reason(
    start_date: datetime = Query(..., description="Data de início do filtro"),
    end_date: datetime = Query(..., description="Data de término do filtro"),
    reason_id: Optional[int] = Query(None, description="ID da categoria para filtrar as transações"),
    db: Session = Depends(get_db)
):
    # Verifica se as datas estão corretas
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="A data de início não pode ser maior que a data de término.")

    
    # Inicia a consulta com o filtro de data
    query = db.query(Transaction).filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date
    )

    # Se reason_id for fornecido, adiciona o filtro correspondente
    if reason_id is not None:
        query = query.filter(Transaction.reason_id == reason_id)

    # Executa a consulta
    readings = query.all()

    # Verifica se há resultados
    if not readings:
        return JSONResponse(
            content={
                "total_weight": 0,
                "total_value": 0,
                "total_transactions": 0,
                "message": "Nenhum registro encontrado para o intervalo e ID de categoria especificados."
            },
            status_code=200
        )
    
    total_weight = sum(reading.weight for reading in readings if reading.weight is not None)
    total_value = sum((reading.weight or 0) * (reading.food.price or 0) for reading in readings if reading.food)
    total_transactions = len(readings)

    return JSONResponse(content={
        "total_weight": total_weight,
        "total_value": total_value,
        "total_transactions": total_transactions
    })

@app.get("/food-waste/foods")
async def get_foods(db: Session = Depends(get_db)):     
    lista_de_alimentos = db.query(Food).all()
    lista_de_alimentos = [alimento.__dict__ for alimento in lista_de_alimentos]
    
    for alimento in lista_de_alimentos:
        alimento.pop('_sa_instance_state')
        # Adiciona o caminho completo da imagem

    print(lista_de_alimentos)
    return JSONResponse(content={
        "foods": lista_de_alimentos
    })


# Função para ler dados da balança
def ler_dados_balança():
    global ultimo_dado_balança, executando
    try:
        ser = serial.Serial(
            porta_serial,
            baudrate,
            bytesize=bits_de_dados,
            parity=paridade,
            stopbits=bits_de_parada,
            timeout=1
        )

        while executando:
            try:
                dados_brutos = ser.read(tamanho_leitura)
                if len(dados_brutos) > 0:
                    dados_filtrados = dados_brutos.replace(b'\x02', b'').replace(b'\x03', b'')
                    try:
                        dados_decodificados = dados_filtrados.decode('utf-8').strip()
                        ultimo_dado_balança = dados_decodificados
                    except UnicodeDecodeError:
                        print("Erro ao decodificar os dados.")
            except serial.SerialException as e:
                print(f"Erro de comunicação: {e}")
                break
    except serial.SerialException as e:
        print(f"Erro ao conectar à porta serial: {e}")
    finally:
        if ser.is_open:
            ser.close()


# Inicia a thread para leitura da balança
thread_balança = threading.Thread(target=ler_dados_balança)
thread_balança.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
