import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(PROJECT_ROOT, '.env')

if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(PROJECT_ROOT, 'src', '.env') # Fallback
    if not os.path.exists(dotenv_path):
        print(f"ERRO CRÍTICO: Arquivo .env não encontrado.")
        exit()
        
load_dotenv(dotenv_path=dotenv_path, encoding='utf-8')
print(f"[ASP Config] Arquivo .env carregado de: {dotenv_path}")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 dias

DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATABASE_FILE = os.path.join(DATA_DIR, 'maia_database.json')
CALENDAR_TOKEN_FILE = os.path.join(DATA_DIR, 'token.json')
CALENDAR_CREDENTIALS_FILE = os.path.join(DATA_DIR, 'credentials.json')

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CALENDAR_ID = 'primary'
TIMEZONE = 'America/Sao_Paulo'

# --- Verificação Crítica ---
if not GEMINI_API_KEY:
    print("ERRO DE CONFIGURAÇÃO: 'GEMINI_API_KEY' não encontrada no .env.")
    exit()
if not JWT_SECRET_KEY:
    print("ERRO DE CONFIGURAÇÃO: 'JWT_SECRET_KEY' não encontrada no .env. A autenticação falhará.")
    exit()
if not os.path.exists(CALENDAR_CREDENTIALS_FILE):
    print(f"AVISO: 'credentials.json' não encontrado em {CALENDAR_CREDENTIALS_FILE}. O agendamento falhará.")