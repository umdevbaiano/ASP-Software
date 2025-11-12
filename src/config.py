import os
from dotenv import load_dotenv

# --- Carregamento Robusto do .env (V60) ---
# Define o caminho raiz do projeto (a pasta que contém a pasta 'src')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(PROJECT_ROOT, '.env')

print(f"[ASP Config] Carregando segredos de: {dotenv_path}")

if not os.path.exists(dotenv_path):
    print(f"ERRO CRÍTICO: Arquivo .env não encontrado em {PROJECT_ROOT}")
    exit()

load_dotenv(dotenv_path=dotenv_path, encoding='utf-8')

# --- Chaves de API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

# --- Constantes de Caminho ---
# (Usamos PROJECT_ROOT para garantir que os caminhos estejam corretos,
# não importa de onde o script seja executado)
CALENDAR_TOKEN_FILE = os.path.join(PROJECT_ROOT, 'token.json')
CALENDAR_CREDENTIALS_FILE = os.path.join(PROJECT_ROOT, 'credentials.json')
ARQUIVO_DADOS_NOTAS = os.path.join(PROJECT_ROOT, 'notes_data.json')

# --- Constantes do Calendar ---
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CALENDAR_ID = 'primary'
TIMEZONE = 'America/Sao_Paulo'

# --- Verificação Crítica ---
if not GEMINI_API_KEY:
    print(f"ERRO DE CONFIGURAÇÃO: A chave 'GEMINI_API_KEY' não foi encontrada em {dotenv_path}.")
    exit()
if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
    print("AVISO: Chaves do Google Search não encontradas no .env. A pesquisa falhará.")
if not os.path.exists(CALENDAR_CREDENTIALS_FILE):
    print(f"AVISO: 'credentials.json' não encontrado em {PROJECT_ROOT}. O agendamento falhará.")