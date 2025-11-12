import os
import json
import uuid
from src.config import ARQUIVO_DADOS_NOTAS

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

# --- FUNÇÃO ATUALIZADA (V57) ---
def gerenciar_notas(operacao: str, title: str = None, content: str = None) -> str:
    """
    Realiza operações CRUD em listas persistentes.
    Operações: 'CREATE_LIST', 'READ_ALL', 'ADD_ITEM' (lida com vírgulas), 
               'DELETE_LIST', 'DELETE_ITEM' (por ID).
    """
    data = _load_data()
    operacao = operacao.upper()

    if operacao == 'CREATE_LIST':
        if not title: return "Erro: Para criar uma lista, é necessário fornecer um 'title'."
        if any(lst['title'].lower() == title.lower() for lst in data['lists']):
            return f"Erro: Já existe uma lista com o título '{title}'. Use 'ADD_ITEM'."
        new_list = {"id": str(uuid.uuid4()), "title": title, "items": []}
        data['lists'].append(new_list)
        if _save_data(data): return f"Sucesso: A lista '{title}' foi criada e armazenada."
        return "Erro: Falha ao salvar os dados após a criação da lista."

    elif operacao == 'READ_ALL':
        if not data['lists']: return "Resultado: Não há listas de notas salvas."
        output = ["--- RESUMO DE LISTAS PERSISTENTES ---"]
        for lst in data['lists']:
            item_count = len(lst['items'])
            output.append(f"\nTítulo: {lst['title']} (Itens: {item_count})")
            for item in lst.get('items', []):
                output.append(f"  - (ID: {item.get('item_id', 'N/A')}) {item.get('text', 'N/A')}")
        output.append("\n--- FIM DO RESUMO ---")
        return "\n".join(output)

    elif operacao == 'ADD_ITEM':
        # --- LÓGICA DE PARSING V57 (Correção de Vírgula) ---
        if not title or not content:
            return "Erro: Para adicionar um item, é necessário fornecer o 'title' da lista e o 'content'."

        list_to_update = next((lst for lst in data['lists'] if lst['title'].lower() == title.lower()), None)
        
        if not list_to_update:
            return f"Erro: A lista '{title}' não foi encontrada. Sugiro 'CREATE_LIST' primeiro."

        # Detecta múltiplos itens (separados por vírgula)
        items_to_add = [item.strip() for item in content.split(',') if item.strip()]
        if not items_to_add:
            return "Erro: O 'content' fornecido estava vazio ou mal formatado."
            
        added_items_feedback = []
        for item_text in items_to_add:
            new_item_id = len(list_to_update.get('items', [])) + 1
            list_to_update.setdefault('items', []).append({"item_id": new_item_id, "text": item_text})
            added_items_feedback.append(item_text)
            
        if _save_data(data):
            feedback_str = ", ".join(added_items_feedback)
            return f"Sucesso: Itens '{feedback_str}' adicionados à lista '{title}'. Agora há {len(list_to_update['items'])} itens."
        return "Erro: Falha ao salvar os dados após a adição do item."
        # --- FIM DA LÓGICA V57 ---

    elif operacao == 'DELETE_LIST':
        if not title: return "Erro: Para excluir uma lista, é necessário fornecer o 'title'."
        initial_count = len(data['lists'])
        data['lists'] = [lst for lst in data['lists'] if lst['title'].lower() != title.lower()]
        
        if len(data['lists']) == initial_count:
            return f"Resultado: Nenhuma lista com o título '{title}' foi encontrada para exclusão."

        if _save_data(data): return f"Sucesso: A lista '{title}' foi removida permanentemente."
        return "Erro: Falha ao salvar os dados após a exclusão da lista."

    # --- NOVA OPERAÇÃO V57 ---
    elif operacao == 'DELETE_ITEM':
        if not title or not content:
            return "Erro: Para excluir um item, é necessário fornecer o 'title' da lista e o 'content' (o ID do item)."
        
        list_to_update = next((lst for lst in data['lists'] if lst['title'].lower() == title.lower()), None)
        if not list_to_update:
            return f"Erro: A lista '{title}' não foi encontrada."

        try:
            item_id_to_delete = int(content)
        except ValueError:
            return f"Erro: O 'content' (ID do item) deve ser um número. O senhor forneceu '{content}'."
            
        initial_item_count = len(list_to_update.get('items', []))
        # Filtra o item
        list_to_update['items'] = [item for item in list_to_update.get('items', []) if item.get('item_id') != item_id_to_delete]
        
        if len(list_to_update.get('items', [])) == initial_item_count:
            return f"Erro: Item com ID {item_id_to_delete} não encontrado na lista '{title}'."

        if _save_data(data):
            return f"Sucesso: Item ID {item_id_to_delete} foi removido da lista '{title}'."
        return "Erro: Falha ao salvar os dados após a exclusão do item."
    # --- FIM DA NOVA OPERAÇÃO ---

    return f"Erro: Operação '{operacao}' desconhecida. Use 'CREATE_LIST', 'READ_ALL', 'ADD_ITEM', 'DELETE_LIST', ou 'DELETE_ITEM'."