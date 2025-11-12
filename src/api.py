# src/api.py (V86 - API Stateful com Sessões)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import sys

from fastapi.middleware.cors import CORSMiddleware # (Mantemos o V66)

# Adiciona a pasta 'src' ao caminho
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Importa o cérebro (Stateless)
try:
    from core_agent import processar_turno_do_chat
except ImportError as e:
    print(f"Erro de API: Não foi possível importar o core_agent. {e}")
    def processar_turno_do_chat(h, p): 
        return h, f"Erro crítico de importação no servidor: {e}"

# Importa as configurações e o NOVO MÓDULO DE PERSISTÊNCIA (V86)
from config import PROJECT_ROOT
import tools.persistence as db # (Importamos todo o módulo V86)

# --- Modelos de Dados (Pydantic) ---

class ChatPromptRequest(BaseModel):
    user_prompt: str
    # O histórico não é mais enviado; usamos o session_id

class SessionCreateRequest(BaseModel):
    title: str = "Novo Chat"

class SessionResponse(BaseModel):
    session_id: str
    title: str

class ChatTurnResponse(BaseModel):
    maia_response: str
    session_id: str
    # Enviamos o histórico atualizado para o frontend sincronizar
    updated_history: List[Dict[str, Any]] 

# --- Inicialização da API ---
app = FastAPI(
    title="ASP - Maia API (V86)",
    description="API para o Assistente Pessoal de Software (Maia), com gerenciamento de sessão.",
    version="0.2.0"
)

# --- Configuração de CORS (V66) ---
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints da API (V86) ---

@app.get("/", summary="Verificação de Status")
def read_root():
    """Verifica se o servidor da Maia está online."""
    return {"status": "Maia (ASP V86 com Sessões) está online e operando."}

# --- ENDPOINTS DE SESSÃO (V86) ---

@app.post("/api/sessions/create", response_model=SessionResponse, summary="Cria um novo chat")
def create_new_session(request: SessionCreateRequest):
    """Cria uma nova sessão de chat vazia no banco de dados."""
    os.chdir(PROJECT_ROOT) # Garante que o DB_FILE seja encontrado
    new_session = db.db_create_session(request.title)
    if not new_session:
        raise HTTPException(status_code=500, detail="Erro ao criar sessão no banco de dados.")
    return SessionResponse(session_id=new_session["session_id"], title=new_session["title"])

@app.get("/api/sessions/list", response_model=List[SessionResponse], summary="Lista todos os chats")
def get_all_sessions():
    """Retorna uma lista de IDs e Títulos de todos os chats (para a Sidebar)."""
    os.chdir(PROJECT_ROOT)
    sessions = db.db_list_sessions()
    return sessions

@app.delete("/api/sessions/{session_id}", summary="Exclui um chat")
def delete_session(session_id: str):
    """Exclui uma sessão de chat completa pelo ID."""
    os.chdir(PROJECT_ROOT)
    if not db.db_delete_session(session_id):
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return {"status": "sucesso", "detail": f"Sessão {session_id} excluída."}

# --- ENDPOINTS DE CHAT (V86) ---

@app.get("/api/chat/{session_id}", response_model=List[Dict[str, Any]], summary="Carrega um histórico de chat")
def get_chat_history(session_id: str):
    """Obtém o histórico completo de um chat específico."""
    os.chdir(PROJECT_ROOT)
    session = db.db_get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    return session["history"]

@app.post("/api/chat/{session_id}", response_model=ChatTurnResponse, summary="Envia um prompt para um chat")
def handle_chat_turn(session_id: str, request: ChatPromptRequest):
    """
    Processa um turno de chat. Carrega o histórico da sessão, 
    envia para o Cérebro (V65), e salva o novo histórico.
    """
    os.chdir(PROJECT_ROOT)
    
    # 1. Carregar o histórico do DB
    session = db.db_get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")
    
    current_history = session["history"]

    # 2. Processar o turno (o Cérebro V65 é stateless)
    updated_history, maia_response_text = processar_turno_do_chat(
        history_list=current_history,
        user_prompt=request.user_prompt
    )

    # 3. Salvar o novo histórico no DB
    if not db.db_update_session_history(session_id, updated_history):
        raise HTTPException(status_code=500, detail="Erro ao salvar o histórico da sessão.")

    # 4. Retornar a resposta
    return ChatTurnResponse(
        maia_response=maia_response_text,
        session_id=session_id,
        updated_history=updated_history
    )