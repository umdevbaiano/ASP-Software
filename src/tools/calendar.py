import os
import re
from datetime import datetime, timedelta
from dateutil import parser 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from src.config import (
    CALENDAR_TOKEN_FILE, CALENDAR_CREDENTIALS_FILE, 
    SCOPES, CALENDAR_ID, TIMEZONE
)

def autenticar_calendar():
    creds = None
    if os.path.exists(CALENDAR_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(CALENDAR_TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CALENDAR_CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                return f"Erro de Autenticação: O arquivo '{CALENDAR_CREDENTIALS_FILE}' não foi encontrado na pasta do projeto."
            except Exception as e: return f"Erro de Autenticação: Ocorreu um erro no fluxo OAuth. Erro: {e}"
        with open(CALENDAR_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def agendar_evento(titulo: str, data_hora_inicio: str, duracao_minutos: int = 60, descricao: str = ''):
    try:
        print(f"[ASP] Tentando agendar: {titulo} em {data_hora_inicio}")
        service_or_error = autenticar_calendar()
        if isinstance(service_or_error, str): return service_or_error
        data_hora_inicio_lower = data_hora_inicio.lower()
        now = datetime.now()
        dias_da_semana = {"segunda": 0, "terça": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sábado": 5, "domingo": 6}
        target_weekday_num = -1
        for dia_str, num in dias_da_semana.items():
            if dia_str in data_hora_inicio_lower: target_weekday_num = num; break
        try:
            start_datetime = parser.parse(data_hora_inicio, fuzzy=True, dayfirst=False, default=now)
            if "amanhã" in data_hora_inicio_lower and start_datetime.date() == now.date():
                 tomorrow = now.date() + timedelta(days=1)
                 start_datetime = start_datetime.replace(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
            if start_datetime.date() == now.date() and target_weekday_num != -1:
                current_weekday_num = start_datetime.weekday() 
                if target_weekday_num != current_weekday_num:
                     days_ahead = (target_weekday_num - current_weekday_num + 7) % 7 
                     start_datetime = start_datetime + timedelta(days=days_ahead)
                else: 
                     if "próxima" in data_hora_inicio_lower or "próximo" in data_hora_inicio_lower:
                          start_datetime = start_datetime + timedelta(days=7)
        except Exception:
            return "Erro: Não consegui interpretar a data e hora fornecidas. Por favor, seja mais explícito (ex: 'amanhã 14:00' ou '2025-11-09 14:00')."
        end_datetime = start_datetime + timedelta(minutes=duracao_minutos)
        event = {'summary': titulo, 'description': descricao, 'start': {'dateTime': start_datetime.isoformat(), 'timeZone': TIMEZONE,}, 'end': {'dateTime': end_datetime.isoformat(), 'timeZone': TIMEZONE,}, 'reminders': {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 24 * 60}, {'method': 'popup', 'minutes': 30},],},}
        event = service_or_error.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        time_format = start_datetime.strftime("%d/%m/%Y às %H:%M")
        event_id_from_creation = event.get('id') 
        return f"Sucesso: Evento '{titulo}' criado para {time_format} na sua agenda. ID do Evento: {event_id_from_creation}. URL: {event.get('htmlLink')}"
    except HttpError as e:
        print(f"[ERRO CRÍTICO DA API CALENDAR] {e}")
        return f"Erro ao criar evento no Calendar: Falha na comunicação com o Google. Erro: {e.resp.status}"
    except Exception as e: return f"Erro inesperado ao agendar: {e}"

def excluir_evento(event_id: str):
    """Exclui um evento do Google Calendar usando seu ID."""
    try:
        print(f"[ASP] Tentando excluir evento com ID: {event_id}")
        service_or_error = autenticar_calendar()
        if isinstance(service_or_error, str): return service_or_error
        service_or_error.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        return f"Sucesso: Evento com ID '{event_id}' excluído da agenda."
    except HttpError as e:
        if e.resp.status == 404: return f"Erro ao excluir: Evento com ID '{event_id}' não encontrado."
        return f"Erro ao excluir evento no Calendar: Falha na comunicação com o Google. Erro: {e.resp.status}"
    except Exception as e: return f"Erro inesperado ao excluir evento: {e}"

def listar_eventos(max_results: int = 10):
    try:
        print(f"[ASP] Tentando listar os {max_results} próximos eventos.")
        service_or_error = autenticar_calendar()
        if isinstance(service_or_error, str): return service_or_error
        now_iso = datetime.utcnow().isoformat() + 'Z' 
        events_result = service_or_error.events().list(
            calendarId=CALENDAR_ID, timeMin=now_iso, maxResults=max_results, singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events: return "Nenhum evento futuro encontrado na sua agenda."
        lista_formatada = ["\n--- EVENTOS AGENDADOS ---"]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            try:
                start_time = datetime.fromisoformat(start.replace('Z', '+00:00')).strftime('%d/%m às %H:%M')
            except ValueError:
                start_time = start 
            lista_formatada.append(f"Título: {event['summary']}\nData/Hora: {start_time}\nID do Evento: {event['id']}\n---")
        return "\n".join(lista_formatada)
    except HttpError as e:
        return f"Erro ao listar eventos no Calendar: Falha na comunicação com o Google. Erro: {e.resp.status}"
    except Exception as e: return f"Erro inesperado ao listar eventos: {e}"