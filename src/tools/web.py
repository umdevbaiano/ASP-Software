import os
import re
import requests
from readability import Document
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.config import GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID

def pesquisar_na_internet(query: str):
    try:
        print(f"[ASP] Pesquisando na web (Google Search) por: {query}")
        
        if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
            return "Erro: As credenciais do Google Search (API Key ou CX ID) não estão configuradas."
            
        service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
        res = service.cse().list(q=query, cx=GOOGLE_SEARCH_ENGINE_ID, num=3).execute()

        def clean_string(s):
            if not s: return ""
            s = re.sub(r'<[^>]+>', '', s); return s.replace('\n', ' ').strip()

        snippets = []
        if 'items' in res:
            for item in res['items']:
                title = clean_string(item.get('title'))
                snippet = clean_string(item.get('snippet'))
                if 'htmlTitle' in item and 'url' in item:
                    item_url = item['url']; title = title + f" (Fonte: {item_url.split('/')[2]})"
                snippets.append(f"Título: {title}\nSnippet: {snippet}\n---")
        if not snippets: return "Nenhum resultado encontrado para a pesquisa."
        final_output = "\n".join(snippets)
        if len(final_output) > 3000: final_output = final_output[:3000] + "..."
        return final_output
    except HttpError as e:
        print(f"[ERRO CRÍTICO DA API] {e}")
        return f"Erro de API do Google Search: A chave de API ou o ID do Mecanismo está incorreto ou o limite de cota foi atingido. Erro: {e.resp.status}"
    except Exception as e: return f"Erro ao tentar pesquisar na internet: {e}"

def analisar_url_e_resumir(url: str) -> str:
    try:
        print(f"[ASP] Analisando o conteúdo da URL: {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        doc = Document(response.text)
        full_html = doc.summary(html_partial=False)
        clean_text = re.sub(r'<[^>]+>', '', full_html)
        clean_text = clean_text.replace('\n', ' ').strip()
        max_length = 20000 
        if len(clean_text) > max_length: clean_text = clean_text[:max_length] + "..."
        if not clean_text: return f"Erro: Não foi possível extrair o conteúdo principal da URL ({url}). O URL pode estar protegido ou ser um arquivo."
        return clean_text
    except requests.exceptions.RequestException as e:
        return f"Erro de Rede: Não foi possível aceder ao URL ({url}). Verifique a conectividade ou o endereço. Erro: {e}"
    except Exception as e: return f"Erro inesperado durante a análise da URL: {e}"