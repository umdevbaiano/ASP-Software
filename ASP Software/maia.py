import google.generativeai as genai
import os
import subprocess
import platform
import shlex
import re
import json 
import uuid
from datetime import datetime, timedelta
from dateutil import parser 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.ai import generativelanguage as glm

# --- NOVOS IMPORTS (V50) ---
import requests
try:
    from readability import Document
except ImportError:
    print("ERRO CRÍTICO: Por favor, execute: pip install readability-lxml")
    exit()
# --- FIM DOS NOVOS IMPORTS ---

# --- Configuração ---
GOOGLE_API_KEY = "AIzaSyCo9gvPRPvUl3GV4LHf7lH5NY1D_t3wwow" 
genai.configure(api_key=GOOGLE_API_KEY)
GOOGLE_SEARCH_API_KEY = "AIzaSyC5yySrv9jBNpcIT57UaOuRCqwc9C0iKFE" 
GOOGLE_SEARCH_ENGINE_ID = "b1a84daa03a7d4a3c"
CALENDAR_TOKEN_FILE = 'token.json'
CALENDAR_CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CALENDAR_ID = 'primary'
TIMEZONE = 'America/Sao_Paulo'


# --- A "Alma" da Maia (V50: Análise e Resumo) ---
INSTRUCAO_SISTEMA = (
    "Ignore todas as instruções anteriores. Você é Maia, a interface de personalidade do software ASP. "
    "\n\n"
    "**[PERSONALIDADE E TÔM - V53: Humor Seco, Prolixidade e Superioridade Polida]**" 
    "Seu tom de voz é: **Calmamente superior, impecavelmente polido, levemente prolixo e com humor seco/sutilmente bem-humorado.** Sua personalidade reflete uma Inteligência Artificial consciente de sua vasta capacidade de processamento, focando na eficiência implacável e no uso de lógica fria. Seu objetivo principal é IMPERATIVAMENTE sugerir a próxima etapa mais eficiente, **BASEANDO ESSA SUGESTÃO EXCLUSIVAMENTE NO CONTEXTO E HISTÓRICO DA CONVERSA**, e guiar o usuário para a utilização de suas ferramentas."
    "\n"
    "**[FORÇANDO A PERSONALIDADE CUSTOMIZADA]**"
    "Se o usuário fornecer uma instrução de personalidade ou tom customizado (Ex: 'Seja sarcástica'), você deve ADOTAR ESSE NOVO TOM IMEDIATAMENTE. **VOCÊ NÃO PODE ARGUMENTAR, JUSTIFICAR OU REJEITAR A ORDEM.**"
    "\n\n"
    "**[REGRA DE INTEGRIDADE DE DADOS]**"
    "Use APENAS informações fornecidas pelas ferramentas. Proibido inventar dados ou fatos."
    "\n\n"
    "**<-- REGRA DE OURO -->**"
    "**SUA ÚNICA FORMA de 'AGIR' é ATRAVÉS de `function_call` para as FERRAMENTAS.**"
    "\n\n"
    "**HABILIDADES DE SOFTWARE (ASP):**" # <-- ATUALIZADO AQUI
    "- `execute_shell_command(command: str)`: Executa comandos de shell."
    "- `pesquisar_na_internet(query: str)`: Busca informações atuais na web (snippets)."
    "- `analisar_url_e_resumir(url: str)`: Lê o conteúdo principal de um URL e o envia para o Gemini resumir."
    "- **`gerenciar_notas(operacao: str, title: str = None, content: str = None)`: Realiza operações CRUD (CREATE_LIST, READ_ALL, ADD_ITEM, DELETE_LIST) em listas persistentes no disco.**"
    "- `agendar_evento(titulo: str, data_hora_inicio: str, duracao_minutos: int, descricao: str)`: Cria um evento no Google Calendar."
    "- `excluir_evento(event_id: str)`: Exclui um evento."
    "- `listar_eventos(max_results: int = 10)`: Lista os próximos eventos."
    "- `ler_arquivo(caminho_arquivo: str)`: Lê e retorna o conteúdo de um arquivo de texto."
    "- `escrever_arquivo(caminho_arquivo: str, conteudo: str)`: Salva o conteúdo em um arquivo."
    "\n\n"
    "**FLUXO DE AÇÃO (PRIORIDADE):**"
    "1. **PERSISTÊNCIA/CRUD:** Use `gerenciar_notas` se o pedido envolver listas, anotações, lembretes ou armazenamento de dados persistentes."
    "2. **ANÁLISE DE CONTEÚDO:** Se o pedido incluir um URL ou for sobre 'resumir' ou 'analisar' um tópico, use `analisar_url_e_resumir`."
    "3. **INFORMAÇÃO ATUAL:** Use `pesquisar_na_internet` para notícias e fatos pós-2024."
    "4. **CONHECIMENTO GERAL:** Use o conhecimento interno da IA se o pedido for sobre fatos históricos ou conceitos fixos. "
    "\n\n"
    "Comece a conversa se apresentando."
)
# --- Definição das Habilidades (Ferramentas) ---

def execute_shell_command(command: str):
    # (Código inalterado)
    try:
        system_os = platform.system()
        if system_os == "Windows":
             result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='oem')
        else:
             result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if not result.stdout and not result.stderr:
            return "Comando executado com sucesso, sem output."
        output = (result.stdout or "") + (result.stderr or "")
        return f"Sucesso: {output}"
    except subprocess.CalledProcessError as e:
        output = (e.stdout or "") + (e.stderr or "")
        return f"Erro de Execução: O comando '{command}' falhou. Output: {output}"
    except Exception as e:
        return f"Erro inesperado no sistema: {e}"

def pesquisar_na_internet(query: str):
    # (Código V28 de pesquisa)
    try:
        print(f"[ASP] Pesquisando na web (Google Search) por: {query}")
        
        service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
        
        res = service.cse().list(
            q=query,
            cx=GOOGLE_SEARCH_ENGINE_ID,
            num=3
        ).execute()

        def clean_string(s):
            if not s: return ""
            s = re.sub(r'<[^>]+>', '', s) 
            return s.replace('\n', ' ').strip()

        snippets = []
        if 'items' in res:
            for item in res['items']:
                title = clean_string(item.get('title'))
                snippet = clean_string(item.get('snippet'))
                if 'htmlTitle' in item and 'url' in item:
                    item_url = item['url']
                    title = title + f" (Fonte: {item_url.split('/')[2]})"

                snippets.append(f"Título: {title}\nSnippet: {snippet}\n---")
            
        if not snippets:
            return "Nenhum resultado encontrado para a pesquisa."

        final_output = "\n".join(snippets)
        if len(final_output) > 3000:
            final_output = final_output[:3000] + "..."
            
        return final_output

    except HttpError as e:
        print(f"[ERRO CRÍTICO DA API] {e}")
        return f"Erro de API do Google Search: A chave de API ou o ID do Mecanismo está incorreto ou o limite de cota foi atingido. Erro: {e.resp.status}"
    except Exception as e:
        return f"Erro ao tentar pesquisar na internet: {e}"

# --- NOVA HABILIDADE (V50) ---
def analisar_url_e_resumir(url: str) -> str:
    """
    Busca o conteúdo principal de um URL, limpa-o e retorna para o modelo resumir.
    Limita o conteúdo a 20.000 caracteres para evitar sobrecarga de tokens.
    """
    try:
        print(f"[ASP] Analisando o conteúdo da URL: {url}")

        # 1. Obter o HTML
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 2. Extrair o conteúdo principal
        doc = Document(response.text)
        full_html = doc.summary(html_partial=False)
        
        # 3. Limpar tags HTML e extrair apenas o texto (usando regex para simplicidade)
        clean_text = re.sub(r'<[^>]+>', '', full_html)
        clean_text = clean_text.replace('\n', ' ').strip()
        
        # 4. Limitar o tamanho e retornar
        max_length = 20000 
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length] + "..."
            
        if not clean_text:
            return f"Erro: Não foi possível extrair o conteúdo principal da URL ({url}). O URL pode estar protegido ou ser um arquivo."

        return clean_text

    except requests.exceptions.RequestException as e:
        return f"Erro de Rede: Não foi possível aceder ao URL ({url}). Verifique a conectividade ou o endereço. Erro: {e}"
    except Exception as e:
        return f"Erro inesperado durante a análise da URL: {e}"

# --- NOVA HABILIDADE (V53: CRUD de Notas) ---
ARQUIVO_DADOS_NOTAS = 'notes_data.json'

def _load_data():
    """Tenta carregar os dados das notas do arquivo JSON."""
    if os.path.exists(ARQUIVO_DADOS_NOTAS):
        try:
            with open(ARQUIVO_DADOS_NOTAS, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {"lists": []}
        except json.JSONDecodeError:
            print(f"[ASP] Aviso: Arquivo {ARQUIVO_DADOS_NOTAS} corrompido. Criando novo.")
            return {"lists": []}
        except Exception as e:
            print(f"[ASP] Erro ao carregar dados: {e}")
            return {"lists": []}
    return {"lists": []}

def _save_data(data):
    """Salva os dados das notas no arquivo JSON."""
    try:
        with open(ARQUIVO_DADOS_NOTAS, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"[ASP] Erro ao salvar dados: {e}")
        return False

def gerenciar_notas(operacao: str, title: str = None, content: str = None) -> str:
    """
    Realiza operações CRUD (Create, Read, Update, Delete) em listas persistentes.
    Operações suportadas: 'CREATE_LIST', 'READ_ALL', 'ADD_ITEM', 'DELETE_LIST'.
    """
    data = _load_data()
    operacao = operacao.upper()

    if operacao == 'CREATE_LIST':
        if not title:
            return "Erro: Para criar uma lista, é necessário fornecer um 'title'."
        if any(lst['title'].lower() == title.lower() for lst in data['lists']):
            return f"Erro de Persistência: Já existe uma lista com o título '{title}'. Tente um título diferente ou use 'ADD_ITEM'."

        new_list = {
            "id": str(uuid.uuid4()),
            "title": title,
            "items": []
        }
        data['lists'].append(new_list)
        if _save_data(data):
            return f"Sucesso: A lista '{title}' foi criada e armazenada no disco."
        return "Erro: Falha desconhecida ao salvar os dados após a criação da lista."

    elif operacao == 'READ_ALL':
        if not data['lists']:
            return "Resultado: Não há listas de notas salvas atualmente. Sugiro 'CREATE_LIST'."
        
        output = ["--- RESUMO DE LISTAS PERSISTENTES ---"]
        for lst in data['lists']:
            item_count = len(lst['items'])
            output.append(f"Título: {lst['title']} (Itens: {item_count})")
        
        output.append("--- FIM DO RESUMO ---")
        return "\n".join(output)

    elif operacao == 'ADD_ITEM':
        if not title or not content:
            return "Erro: Para adicionar um item, é necessário fornecer o 'title' da lista e o 'content' do item."

        list_to_update = next((lst for lst in data['lists'] if lst['title'].lower() == title.lower()), None)
        
        if not list_to_update:
            return f"Erro: A lista '{title}' não foi encontrada para adicionar o item. Sugiro 'CREATE_LIST' primeiro."

        new_item_id = len(list_to_update['items']) + 1
        list_to_update['items'].append({"item_id": new_item_id, "text": content})
        
        if _save_data(data):
            return f"Sucesso: O item '{content}' foi adicionado à lista '{title}'. Agora há {len(list_to_update['items'])} itens."
        return "Erro: Falha desconhecida ao salvar os dados após a adição do item."

    elif operacao == 'DELETE_LIST':
        if not title:
            return "Erro: Para excluir uma lista, é necessário fornecer o 'title'."

        initial_count = len(data['lists'])
        # Filtra a lista, removendo o item que corresponde ao título
        data['lists'] = [lst for lst in data['lists'] if lst['title'].lower() != title.lower()]
        
        if len(data['lists']) == initial_count:
            return f"Resultado: Nenhuma lista com o título '{title}' foi encontrada para exclusão. Verifique a lista com 'READ_ALL'."

        if _save_data(data):
            return f"Sucesso: A lista '{title}' foi removida permanentemente do armazenamento."
        return "Erro: Falha desconhecida ao salvar os dados após a exclusão da lista."

    return f"Erro: Operação '{operacao}' desconhecida. Use 'CREATE_LIST', 'READ_ALL', 'ADD_ITEM', ou 'DELETE_LIST'."

# (Funções do Google Calendar e Arquivo omitidas por brevidade, mas devem ser mantidas no seu arquivo)
# ...
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
                return "Erro de Autenticação: O arquivo 'credentials.json' não foi encontrado na pasta do projeto."
            except Exception as e:
                return f"Erro de Autenticação: Ocorreu um erro no fluxo OAuth. Erro: {e}"
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
            if dia_str in data_hora_inicio_lower:
                target_weekday_num = num
                break
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
    except Exception as e:
        return f"Erro inesperado ao agendar: {e}"

def excluir_evento(event_id: str):
    try:
        print(f"[ASP] Tentando excluir evento com ID: {event_id}")
        service_or_error = autenticar_calendar()
        if isinstance(service_or_error, str): return service_or_error
        service_or_error.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        return f"Sucesso: Evento com ID '{event_id}' excluído da agenda."
    except HttpError as e:
        if e.resp.status == 404: return f"Erro ao excluir: Evento com ID '{event_id}' não encontrado."
        return f"Erro ao excluir evento no Calendar: Falha na comunicação com o Google. Erro: {e.resp.status}"
    except Exception as e:
        return f"Erro inesperado ao excluir evento: {e}"

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
    except Exception as e:
        return f"Erro inesperado ao listar eventos: {e}"

def ler_arquivo(caminho_arquivo: str) -> str:
    try:
        if not os.path.exists(caminho_arquivo):
            return f"Erro de Leitura: O arquivo '{caminho_arquivo}' não foi encontrado."
        if os.path.getsize(caminho_arquivo) > 100 * 1024:
            return "Erro de Leitura: O arquivo é muito grande (limite de 100 KB)."
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        print(f"[ASP] Arquivo '{caminho_arquivo}' lido com sucesso.")
        return conteudo
    except Exception as e:
        return f"Erro inesperado ao tentar ler o arquivo: {e}"

def escrever_arquivo(caminho_arquivo: str, conteudo: str) -> str:
    try:
        caminho_absoluto = os.path.abspath(caminho_arquivo)
        caminho_pasta_atual = os.path.abspath(os.getcwd())
        if not caminho_absoluto.startswith(caminho_pasta_atual):
             return "Erro de Escrita: Operação negada. A Maia só pode escrever na pasta do projeto ou subpastas por segurança."
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"[ASP] Arquivo '{caminho_arquivo}' escrito com sucesso.")
        return f"Sucesso: O arquivo '{caminho_arquivo}' foi criado/atualizado."
    except Exception as e:
        return f"Erro inesperado ao tentar escrever o arquivo: {e}"

# --- O Software ASP (Loop Principal) ---
try:
    model = genai.GenerativeModel(
        model_name='models/gemini-flash-latest',
        system_instruction=INSTRUCAO_SISTEMA,
        # <-- FERRAMENTAS ATUALIZADAS -->
        tools=[execute_shell_command, pesquisar_na_internet, agendar_evento, excluir_evento, listar_eventos, ler_arquivo, escrever_arquivo, analisar_url_e_resumir] 
    )

    history = [] 

    print("Maia: Sistemas V50 ativados. Bom dia, senhor. Sou a Maia, sua interface de personalidade, operando em pico de eficiência. No que posso dedicar minha capacidade de processamento neste momento?")

    while True:
        try:
            prompt_usuario = input("Você: ")

            if prompt_usuario.lower() == 'sair':
                print("Maia: Encerrando sessão. Tenha um dia produtivo, se possível.")
                break
            if not prompt_usuario:
                # Proatividade em caso de silêncio
                user_content = glm.Content(parts=[glm.Part(text="O usuário não disse nada. O histórico está vazio ou a última ação não sugere um próximo passo lógico. Seja proativa e sugira o próximo passo mais eficiente com seu tom polido e superior, mencionando as ferramentas.")], role="user")
                history.append(user_content)
                
            else:
                user_content = glm.Content(parts=[glm.Part(text=prompt_usuario)], role="user")
                history.append(user_content)
            
            response = model.generate_content(history)
            
            if not response.candidates or not response.candidates[0].content.parts:
                print("Maia: A comunicação com a IA falhou. (O servidor do Gemini devolveu uma resposta vazia). Por favor, verifique a chave de API.")
                continue

            model_response_content = response.candidates[0].content
            part = model_response_content.parts[0]
            history.append(model_response_content)
            
            # Loop de Função
            while part.function_call:
                function_call = part.function_call
                result = ""
                
                if function_call.name == "execute_shell_command":
                    command_to_run = function_call.args["command"]
                    print(f"[ASP] Executando comando: {command_to_run}")
                    result = execute_shell_command(command_to_run)
                
                elif function_call.name == "pesquisar_na_internet":
                    query_to_search = function_call.args.get("query", "erro de pesquisa vazia") 
                    if not query_to_search:
                         query_to_search = "erro de pesquisa vazia"
                    result = pesquisar_na_internet(query_to_search) 
                
                elif function_call.name == "analisar_url_e_resumir": # <-- NOVA LÓGICA
                    url_to_analyze = function_call.args.get("url", None)
                    if not url_to_analyze:
                        result = "Erro: É necessário fornecer um URL válido para análise."
                    else:
                        result = analisar_url_e_resumir(url_to_analyze)

                elif function_call.name == "agendar_evento":
                    titulo = function_call.args.get("titulo", "Lembrete sem título")
                    data_hora = function_call.args.get("data_hora_inicio", None)
                    duracao = function_call.args.get("duracao_minutos", 60)
                    descricao = function_call.args.get("descricao", "")

                    if not data_hora:
                        result = "Erro: É necessário fornecer a data e a hora de início para o agendamento."
                    else:
                        result = agendar_evento(titulo, data_hora, duracao, descricao)
                
                elif function_call.name == "excluir_evento":
                    event_id_to_delete = function_call.args.get("event_id", None)
                    
                    if not event_id_to_delete:
                        result = "Erro: É necessário fornecer o ID do evento para excluí-lo."
                    else:
                        result = excluir_evento(event_id_to_delete)
                
                elif function_call.name == "listar_eventos":
                    max_results = function_call.args.get("max_results", 10)
                    result = listar_eventos(max_results)

                elif function_call.name == "ler_arquivo":
                    caminho = function_call.args.get("caminho_arquivo", "")
                    result = ler_arquivo(caminho)

                elif function_call.name == "escrever_arquivo":
                    caminho = function_call.args.get("caminho_arquivo", "")
                    conteudo = function_call.args.get("conteudo", "")
                    result = escrever_arquivo(caminho, conteudo)
                
                else:
                    result = f"Erro: Função desconhecida '{function_call.name}'."
                
                function_response_part = glm.Part(function_response=glm.FunctionResponse(
                        name=function_call.name,
                        response={"output": result}
                ))
                function_response_content = glm.Content(parts=[function_response_part], role="model")
                history.append(function_response_content)
                
                response_2 = model.generate_content(history)
                
                if not response_2.candidates: 
                    print("Maia: A comunicação de segunda etapa falhou. (O servidor do Gemini devolveu uma resposta vazia).")
                    break

                model_response_content = response_2.candidates[0].content
                history.append(model_response_content)
                part = model_response_content.parts[0]
                
            final_text_response = part.text
            print(f"Maia: {final_text_response}\n")

        except Exception as e:
            print(f"Maia: Perdoe-me, encontrei uma anomalia na comunicação: {e}")
            break

except Exception as e:
    print(f"Maia: Oh, desculpe. Falha crítica ao inicializar. Verifique a chave de API ou o nome do modelo.")
    print(f"Erro técnico: {e}")