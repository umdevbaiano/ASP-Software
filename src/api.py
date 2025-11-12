# src/api.py (V66 - Habilitando CORS)
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import sys

# --- NOVO (V66): Importar o Middleware de CORS ---
from fastapi.middleware.cors import CORSMiddleware

# Adiciona a pasta 'src' ao caminho
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Importa o cérebro refatorado
try:
    from core_agent import processar_turno_do_chat
except ImportError as e:
    print(f"Erro de API: Não foi possível importar o core_agent. {e}")
    def processar_turno_do_chat(h, p): 
        return h, f"Erro crítico de importação no servidor: {e}"

# Importa as configurações (para definir caminhos de dados)
from config import PROJECT_ROOT

# --- Modelos de Dados (Pydantic) ---
class ChatRequest(BaseModel):
    user_prompt: str
    history: List[Dict[str, Any]] 

class ChatResponse(BaseModel):
    maia_response: str
    updated_history: List[Dict[str, Any]]

# --- Inicialização da API ---
app = FastAPI(
    title="ASP - Maia API",
    description="API para o Assistente Pessoal de Software (Maia), com lógica de IA e ferramentas.",
    version="0.1.0"
)

# --- CONFIGURAÇÃO DE CORS (V66) ---

# Define quais "origens" (websites) podem fazer requisições para esta API.
origins = [
    "http://localhost:3000",  # O endereço padrão do React/Next.js (Frontend)
    "http://localhost:3001",  # Um endereço alternativo comum
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)
# --- FIM DA CONFIGURAÇÃO DE CORS ---


# --- Endpoints da API ---

@app.get("/", summary="Verificação de Status")
def read_root():
    """Verifica se o servidor da Maia está online."""
    return {"status": "Maia (ASP V66 com CORS) está online e operando em máxima eficiência."}

@app.post("/chat", response_model=ChatResponse, summary="Processar Interação com a Maia")
def handle_chat_turn(request: ChatRequest):
    """
    Recebe o prompt do usuário e o histórico da conversa (JSON/Dicts),
    processa o turno (incluindo chamadas de ferramentas) e retorna 
    a resposta da Maia e o histórico atualizado (JSON/Dicts).
    """
    
    os.chdir(PROJECT_ROOT)
    
    updated_history, maia_response_text = processar_turno_do_chat(
        history_list=request.history,
        user_prompt=request.user_prompt
    )

    return ChatResponse(
        maia_response=maia_response_text,
        updated_history=updated_history
    )