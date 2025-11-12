import os
import json
import uuid
from src.config import ARQUIVO_DADOS_NOTAS # Importa o caminho do config

def _load_data():
    """Tenta carregar os dados das notas do arquivo JSON."""
    if os.path.exists(ARQUIVO_DADOS_NOTAS):
        try:
            with open(ARQUIVO_DADOS_NOTAS, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "lists" not in data or not isinstance(data["lists"], list):
                    return {"lists": []}
                return data
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
    """Realiza operações CRUD (CREATE_LIST, READ_ALL, ADD_ITEM, DELETE_LIST) em listas persistentes."""
    data = _load_data()
    operacao = operacao.upper()

    if operacao == 'CREATE_LIST':
        if not title: return "Erro: Para criar uma lista, é necessário fornecer um 'title'."
        if any(lst['title'].lower() == title.lower() for lst in data['lists']):
            return f"Erro de Persistência: Já existe uma lista com o título '{title}'. Tente um título diferente ou use 'ADD_ITEM'."
        new_list = {"id": str(uuid.uuid4()), "title": title, "items": []}
        data['lists'].append(new_list)
        if _save_data(data): return f"Sucesso: A lista '{title}' foi criada e armazenada no disco."
        return "Erro: Falha desconhecida ao salvar os dados após a criação da lista."

    elif operacao == 'READ_ALL':
        if not data['lists']: return "Resultado: Não há listas de notas salvas atualmente. Sugiro 'CREATE_LIST'."
        output = ["--- RESUMO DE LISTAS PERSISTENTES ---"]
        for lst in data['lists']:
            item_count = len(lst['items'])
            output.append(f"Título: {lst['title']} (Itens: {item_count})")
            for item in lst['items']:
                output.append(f"  - Item {item.get('item_id', 'N/A')}: {item.get('text', 'N/A')}")
        output.append("--- FIM DO RESUMO ---")
        return "\n".join(output)

    elif operacao == 'ADD_ITEM':
        if not title or not content: return "Erro: Para adicionar um item, é necessário fornecer o 'title' da lista e o 'content' do item."
        list_to_update = next((lst for lst in data['lists'] if lst['title'].lower() == title.lower()), None)
        if not list_to_update: return f"Erro: A lista '{title}' não foi encontrada para adicionar o item. Sugiro 'CREATE_LIST' primeiro."
        new_item_id = len(list_to_update.get('items', [])) + 1
        list_to_update.setdefault('items', []).append({"item_id": new_item_id, "text": content})
        if _save_data(data): return f"Sucesso: O item '{content}' foi adicionado à lista '{title}'. Agora há {len(list_to_update['items'])} itens."
        return "Erro: Falha desconhecida ao salvar os dados após a adição do item."

    elif operacao == 'DELETE_LIST':
        if not title: return "Erro: Para excluir uma lista, é necessário fornecer o 'title'."
        initial_count = len(data['lists'])
        data['lists'] = [lst for lst in data['lists'] if lst['title'].lower() != title.lower()]
        if len(data['lists']) == initial_count:
            return f"Resultado: Nenhuma lista com o título '{title}' foi encontrada para exclusão. Verifique a lista com 'READ_ALL'."
        if _save_data(data): return f"Sucesso: A lista '{title}' foi removida permanentemente do armazenamento."
        return "Erro: Falha desconhecida ao salvar os dados após a exclusão da lista."
    return f"Erro: Operação '{operacao}' desconhecida. Use 'CREATE_LIST', 'READ_ALL', 'ADD_ITEM', ou 'DELETE_LIST'."