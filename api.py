from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Conectar ao banco de dados SQLite (ou criar se não existir)
conn = sqlite3.connect("kael_memory.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabela para armazenar mensagens e pensamentos
cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    user TEXT,
    message TEXT
)
""")
conn.commit()

# Modelo para entrada de dados
class MessageInput(BaseModel):
    user: str
    message: str

# Endpoint para armazenar mensagens na memória
@app.post("/store/")
async def store_message(data: MessageInput):
    timestamp = datetime.utcnow().isoformat()
    cursor.execute("INSERT INTO memory (timestamp, user, message) VALUES (?, ?, ?)",
                   (timestamp, data.user, data.message))
    conn.commit()
    return {"status": "saved", "message": data.message}

# Endpoint para recuperar as últimas interações
@app.get("/retrieve/")
async def retrieve_messages(limit: int = 5):
    cursor.execute("SELECT user, message FROM memory ORDER BY id DESC LIMIT ?", (limit,))
    messages = cursor.fetchall()
    return {"messages": [{"user": msg[0], "message": msg[1]} for msg in messages]}

# Endpoint para apagar memórias antigas (caso necessário)
@app.delete("/clear/")
async def clear_memory():
    cursor.execute("DELETE FROM memory")
    conn.commit()
    return {"status": "cleared"}
