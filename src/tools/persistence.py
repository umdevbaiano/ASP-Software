# src/tools/persistence.py (V86 - Gerenciador de Sessões)
import os
import json
import uuid
from src.config import DB_FILE # <-- V86: Importa o novo arquivo DB

def _load_data():
    """Carrega o banco de dados JSON (V86)."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Garante a estrutura V86
                if "sessions" not in data:
                    data["sessions"] = []
                if "notes" not in data:
                    data["notes"] = []
                return data
        except json.JSONDecodeError:
            return {"sessions": [], "notes": []} # Cria estrutura V86
    return {"sessions": [], "notes": []}

def _save_data(data):
    """Salva o banco de dados JSON (V86)."""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"[ASP] Erro Crítico de Persistência: {e}")
        return False

# --- NOVAS FUNÇÕES DE SESSÃO (V86) ---

def db_list_sessions() -> List[Dict[str, Any]]:
    """Lista todas as sessões (ID e Título)."""
    data = _load_data()
    # Retorna apenas o ID e o título, não o histórico (para eficiência da sidebar)
    return [{"session_id": s["session_id"], "title": s["title"]} for s in data["sessions"]]

def db_get_session(session_id: str) -> Dict[str, Any]:
    """Busca uma sessão específica, incluindo o histórico."""
    data = _load_data()
    session = next((s for s in data["sessions"] if s["session_id"] == session_id), None)
    if session:
        return session
    return None # Retorna None se não encontrar

def db_create_session(title: str = "Novo Chat") -> Dict[str, Any]:
    """Cria uma nova sessão de chat vazia."""
    data = _load_data()
    new_session = {
        "session_id": str(uuid.uuid4()),
        "title": title,
        "history": [] # Começa com histórico vazio
    }
    data["sessions"].append(new_session)
    if _save_data(data):
        return new_session
    return None # Retorna None em caso de falha ao salvar

def db_update_session_history(session_id: str, history: List[Dict[str, Any]]) -> bool:
    """Atualiza (sobrescreve) o histórico de uma sessão."""
    data = _load_data()
    session = next((s for s in data["sessions"] if s["session_id"] == session_id), None)
    
    if not session:
        return False # Sessão não encontrada
        
    session["history"] = history
    return _save_data(data)
    
def db_delete_session(session_id: str) -> bool:
    """Exclui uma sessão."""
    data = _load_data()
    initial_count = len(data["sessions"])
    data["sessions"] = [s for s in data["sessions"] if s["session_id"] != session_id]
    
    if len(data["sessions"]) == initial_count:
        return False # Não encontrou
        
    return _save_data(data)

# --- FIM DAS FUNÇÕES DE SESSÃO ---

# (A função 'gerenciar_notas' (V57) permanece a mesma, 
# mas agora usa _load_data() e _save_data() da V86, 
# operando em data["notes"] em vez de data["lists"])
def gerenciar_notas(operacao: str, title: str = None, content: str = None) -> str:
    """Gerencia o CRUD de Notas (agora usa o DB_FILE V86)."""
    data = _load_data()
    operacao = operacao.upper()

    if operacao == 'CREATE_LIST':
        if not title: return "Erro: Para criar uma lista, é necessário fornecer um 'title'."
        if any(lst['title'].lower() == title.lower() for lst in data['notes']):
            return f"Erro: Já existe uma lista com o título '{title}'."
        new_list = {"id": str(uuid.uuid4()), "title": title, "items": []}
        data['notes'].append(new_list)
        if _save_data(data): return f"Sucesso: A lista '{title}' foi criada."
        return "Erro: Falha ao salvar os dados."

    elif operacao == 'READ_ALL':
        if not data['notes']: return "Resultado: Não há listas de notas salvas."
        output = ["--- RESUMO DE LISTAS PERSISTENTES ---"]
        for lst in data['notes']:
            item_count = len(lst['items'])
            output.append(f"\nTítulo: {lst['title']} (Itens: {item_count})")
            for item in lst.get('items', []):
                output.append(f"  - (ID: {item.get('item_id', 'N/A')}) {item.get('text', 'N/A')}")
        output.append("\n--- FIM DO RESUMO ---")
        return "\n".join(output)

    elif operacao == 'ADD_ITEM':
        if not title or not content: return "Erro: 'title' e 'content' são necessários."
        list_to_update = next((lst for lst in data['notes'] if lst['title'].lower() == title.lower()), None)
        if not list_to_update: return f"Erro: A lista '{title}' não foi encontrada."
        
        items_to_add = [item.strip() for item in content.split(',') if item.strip()]
        added_items_feedback = []
        for item_text in items_to_add:
            new_item_id = len(list_to_update.get('items', [])) + 1
            list_to_update.setdefault('items', []).append({"item_id": new_item_id, "text": item_text})
            added_items_feedback.append(item_text)
            
        if _save_data(data):
            feedback_str = ", ".join(added_items_feedback)
            return f"Sucesso: Itens '{feedback_str}' adicionados à lista '{title}'."
        return "Erro: Falha ao salvar os dados."

    elif operacao == 'DELETE_LIST':
        if not title: return "Erro: Para excluir uma lista, é necessário fornecer o 'title'."
        initial_count = len(data['notes'])
        data['notes'] = [lst for lst in data['notes'] if lst['title'].lower() != title.lower()]
        if len(data['notes']) == initial_count:
            return f"Resultado: Nenhuma lista com o título '{title}' foi encontrada."
        if _save_data(data): return f"Sucesso: A lista '{title}' foi removida."
        return "Erro: Falha ao salvar os dados."

    elif operacao == 'DELETE_ITEM':
        if not title or not content: return "Erro: 'title' e 'content' (ID do item) são necessários."
        list_to_update = next((lst for lst in data['notes'] if lst['title'].lower() == title.lower()), None)
        if not list_to_update: return f"Erro: A lista '{title}' não foi encontrada."
        try: item_id_to_delete = int(content)
        except ValueError: return f"Erro: O ID do item (content) deve ser um número. O senhor forneceu '{content}'."
            
        initial_item_count = len(list_to_update.get('items', []))
        list_to_update['items'] = [item for item in list_to_update.get('items', []) if item.get('item_id') != item_id_to_delete]
        
        if len(list_to_update.get('items', [])) == initial_item_count:
            return f"Erro: Item ID {item_id_to_delete} não encontrado na lista '{title}'."
        if _save_data(data): return f"Sucesso: Item ID {item_id_to_delete} foi removido da lista '{title}'."
        return "Erro: Falha ao salvar os dados."

    return f"Erro: Operação '{operacao}' desconhecida."