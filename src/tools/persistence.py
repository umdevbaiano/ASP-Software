import os
import json
import uuid
from src.config import DATABASE_FILE
from src.auth import get_password_hash
from typing import List, Dict, Any

def _load_data():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "users" not in data:
                    data["users"] = []
                return data
        except json.JSONDecodeError:
            return {"users": []}
    return {"users": []}

def _save_data(data):
    try:
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"[ASP] Erro Crítico de Persistência: {e}")
        return False

def db_get_user_by_email(email: str) -> Dict[str, Any]:
    data = _load_data()
    return next((user for user in data["users"] if user["email"] == email), None)

def db_create_user(email: str, password: str, full_name: str) -> Dict[str, Any]:
    data = _load_data()
    
    if db_get_user_by_email(email):
        return None

    hashed_password = get_password_hash(password)
    
    new_user = {
        "user_id": str(uuid.uuid4()),
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed_password,
        "sessions": [],
        "notes": []
    }
    
    data["users"].append(new_user)
    if _save_data(data):
        return new_user
    return None

def db_list_sessions(user_id: str) -> List[Dict[str, Any]]:
    data = _load_data()
    user = next((u for u in data["users"] if u["user_id"] == user_id), None)
    if not user:
        return []
    return [{"session_id": s["session_id"], "title": s["title"]} for s in user["sessions"]]

def db_get_session(user_id: str, session_id: str) -> Dict[str, Any]:
    data = _load_data()
    user = next((u for u in data["users"] if u["user_id"] == user_id), None)
    if not user:
        return None
    session = next((s for s in user["sessions"] if s["session_id"] == session_id), None)
    return session

def db_create_session(user_id: str, title: str = "Novo Chat") -> Dict[str, Any]:
    """Cria uma nova sessão para um usuário."""
    data = _load_data()
    user = next((u for u in data["users"] if u["user_id"] == user_id), None)
    if not user:
        return None

    new_session = {
        "session_id": str(uuid.uuid4()),
        "title": title,
        "history": [] 
    }
    user["sessions"].append(new_session)
    if _save_data(data):
        return new_session
    return None 

def db_update_session_history(user_id: str, session_id: str, history: List[Dict[str, Any]]) -> bool:
    data = _load_data()
    user = next((u for u in data["users"] if u["user_id"] == user_id), None)
    if not user:
        return False
        
    session = next((s for s in user["sessions"] if s["session_id"] == session_id), None)
    if not session:
        return False 
        
    session["history"] = history
    return _save_data(data)
    
def db_delete_session(user_id: str, session_id: str) -> bool:
    data = _load_data()
    user = next((u for u in data["users"] if u["user_id"] == user_id), None)
    if not user:
        return False
        
    initial_count = len(user["sessions"])
    user["sessions"] = [s for s in user["sessions"] if s["session_id"] != session_id]
    
    if len(user["sessions"]) == initial_count:
        return False 
        
    return _save_data(data)

def gerenciar_notas(user_id: str, operacao: str, title: str = None, content: str = None) -> str:
    data = _load_data()
    user = next((u for u in data["users"] if u["user_id"] == user_id), None)
    if not user:
        return "Erro: Usuário não encontrado."
        
    operacao = operacao.upper()

    if operacao == 'CREATE_LIST':
        if not title: return "Erro: 'title' é necessário."
        if any(lst['title'].lower() == title.lower() for lst in user['notes']):
            return f"Erro: A lista '{title}' já existe."
        new_list = {"id": str(uuid.uuid4()), "title": title, "items": []}
        user['notes'].append(new_list)
        if _save_data(data): return f"Sucesso: A lista '{title}' foi criada."
        return "Erro: Falha ao salvar."

    elif operacao == 'READ_ALL':
        if not user['notes']: return "Resultado: Não há listas de notas salvas."
        output = ["--- RESUMO DE LISTAS PERSISTENTES ---"]
        for lst in user['notes']:
            item_count = len(lst['items'])
            output.append(f"\nTítulo: {lst['title']} (Itens: {item_count})")
            for item in lst.get('items', []):
                output.append(f"  - (ID: {item.get('item_id', 'N/A')}) {item.get('text', 'N/A')}")
        output.append("\n--- FIM DO RESUMO ---")
        return "\n".join(output)

    elif operacao == 'ADD_ITEM':
        if not title or not content: return "Erro: 'title' e 'content' são necessários."
        list_to_update = next((lst for lst in user['notes'] if lst['title'].lower() == title.lower()), None)
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
        if not title: return "Erro: 'title' é necessário."
        initial_count = len(user['notes'])
        user['notes'] = [lst for lst in user['notes'] if lst['title'].lower() != title.lower()]
        if len(user['notes']) == initial_count:
            return f"Resultado: Nenhuma lista com o título '{title}' foi encontrada."
        if _save_data(data): return f"Sucesso: A lista '{title}' foi removida."
        return "Erro: Falha ao salvar os dados."

    elif operacao == 'DELETE_ITEM':
        if not title or not content: return "Erro: 'title' e 'content' (ID do item) são necessários."
        list_to_update = next((lst for lst in user['notes'] if lst['title'].lower() == title.lower()), None)
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