# src/api.py (V95 - Imports Absolutos)
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import sys

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm 


from src.core_agent import processar_turno_do_chat_com_nome_de_usuario
from src.config import PROJECT_ROOT
from src.tools import persistence as db
from src.auth import (
        create_access_token, 
        get_current_user, 
        verify_password,
        decode_token 
    )

class ChatPromptRequest(BaseModel): 
    user_prompt: str

class SessionCreateRequest(BaseModel): 
    title: str = "Novo Chat"

class SessionResponse(BaseModel): 
    session_id: str
    title: str

class ChatTurnResponse(BaseModel): 
    maia_response: str
    session_id: str
    updated_history: List[Dict[str, Any]] 

class UserCreateRequest(BaseModel): 
    email: str
    password: str
    full_name: str

class UserResponse(BaseModel): 
    email: str
    full_name: str

class TokenResponse(BaseModel): 
    access_token: str
    token_type: str

app = FastAPI(
    title="ASP - Maia API (V95)",
    description="API para o Assistente Pessoal de Software (Maia), com autenticação de usuário.",
    version="0.3.1"
)
origins = ["http://localhost:3000", "http://localhost:3001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Verificação de Status")
def read_root():
    return {"status": "Maia (ASP V95 com Imports Corrigidos) está online e operando."}

@app.post("/api/auth/register", response_model=UserResponse, summary="Cria um novo usuário")
def register_user(user_data: UserCreateRequest):
    os.chdir(PROJECT_ROOT)
    existing_user = db.db_get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Este email já está registrado.")
    user = db.db_create_user(email=user_data.email, password=user_data.password, full_name=user_data.full_name)
    if not user:
        raise HTTPException(status_code=500, detail="Erro interno ao criar o usuário.")
    return UserResponse(email=user["email"], full_name=user["full_name"])

@app.post("/api/auth/login", response_model=TokenResponse, summary="Login e obtenção de Token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    os.chdir(PROJECT_ROOT)
    user = db.db_get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos.", headers={"WWW-Authenticate": "Bearer"},)
    access_token = create_access_token(data={"sub": user["email"]})
    return TokenResponse(access_token=access_token, token_type="bearer")

@app.post("/api/sessions/create", response_model=SessionResponse, summary="Cria um novo chat (Protegido)")
def create_new_session(
    request: SessionCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    os.chdir(PROJECT_ROOT) 
    user_id = current_user["user_id"]
    new_session = db.db_create_session(user_id=user_id, title=request.title)
    if not new_session:
        raise HTTPException(status_code=500, detail="Erro ao criar sessão no banco de dados.")
    return SessionResponse(session_id=new_session["session_id"], title=new_session["title"])

@app.get("/api/sessions/list", response_model=List[SessionResponse], summary="Lista os chats do usuário (Protegido)")
def get_all_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    os.chdir(PROJECT_ROOT)
    user_id = current_user["user_id"]
    sessions = db.db_list_sessions(user_id=user_id)
    return sessions

@app.delete("/api/sessions/{session_id}", summary="Exclui um chat (Protegido)")
def delete_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    os.chdir(PROJECT_ROOT)
    user_id = current_user["user_id"]
    if not db.db_delete_session(user_id=user_id, session_id=session_id):
        raise HTTPException(status_code=404, detail="Sessão não encontrada ou não pertence ao usuário.")
    return {"status": "sucesso", "detail": f"Sessão {session_id} excluída."}

@app.get("/api/chat/{session_id}", response_model=List[Dict[str, Any]], summary="Carrega um histórico de chat (Protegido)")
def get_chat_history(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    os.chdir(PROJECT_ROOT)
    user_id = current_user["user_id"]
    session = db.db_get_session(user_id=user_id, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada ou não pertence ao usuário.")
    return session["history"]

@app.post("/api/chat/{session_id}", response_model=ChatTurnResponse, summary="Envia um prompt para um chat (Protegido)")
def handle_chat_turn(
    session_id: str, 
    request: ChatPromptRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    os.chdir(PROJECT_ROOT)
    user_id = current_user["user_id"]
    user_name = current_user["full_name"] 
    
    session = db.db_get_session(user_id=user_id, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada ou não pertence ao usuário.")
    
    current_history = session["history"]

    updated_history, maia_response_text = processar_turno_do_chat_com_nome_de_usuario(
        history_list=current_history,
        user_prompt=request.user_prompt,
        user_name=user_name
    )

    if not db.db_update_session_history(user_id=user_id, session_id=session_id, history=updated_history):
        raise HTTPException(status_code=500, detail="Erro ao salvar o histórico da sessão.")

    return ChatTurnResponse(
        maia_response=maia_response_text,
        session_id=session_id,
        updated_history=updated_history
    )