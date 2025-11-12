# src/config.py (V86)

import os
from dotenv import load_dotenv

# --- Carregamento Robusto do .env (V60) ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(PROJECT_ROOT, '.env')

# (Verificações de 'print' e 'load_dotenv' omitidas por brevidade, mas devem ser mantidas)
load_dotenv(dotenv_path=dotenv_path, encoding='utf-8')

# --- Chaves de API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

# --- CORREÇÃO V86: Caminhos de Dados e Configuração ---
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- ARQUIVO DE BANCO DE DADOS (V86) ---
# Este JSON armazenará TODAS as sessões e notas.
DB_FILE = os.path.join(DATA_DIR, 'maia_database.json') 

# Arquivos de autenticação (Inalterados)
CALENDAR_TOKEN_FILE = os.path.join(DATA_DIR, 'token.json')
CALENDAR_CREDENTIALS_FILE = os.path.join(DATA_DIR, 'credentials.json')

# --- Constantes do Calendar (Inalteradas) ---
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CALENDAR_ID = 'primary'
TIMEZONE = 'America/Sao_Paulo'

# --- Verificação Crítica (Inalterada) ---
if not GEMINI_API_KEY:
    print(f"ERRO DE CONFIGURAÇÃO: A chave 'GEMINI_API_KEY' não foi encontrada em {dotenv_path}.")
    exit()
# (Restante das verificações)