import google.generativeai as genai
from google.ai import generativelanguage as glm
import os
from typing import List, Dict, Any

from src.config import GEMINI_API_KEY
from src.system_prompt import INSTRUCAO_SISTEMA_BASE 
from src.tools.system import execute_shell_command, ler_arquivo, escrever_arquivo
from src.tools.persistence import gerenciar_notas
from src.tools.web import pesquisar_na_internet, analisar_url_e_resumir
from src.tools.calendar import agendar_evento, excluir_evento, listar_eventos

def initialize_model(system_instruction: str):
    genai.configure(api_key=GEMINI_API_KEY)
    all_tools = [
        execute_shell_command, pesquisar_na_internet, agendar_evento, 
        excluir_evento, listar_eventos, ler_arquivo, escrever_arquivo, 
        analisar_url_e_resumir, gerenciar_notas
    ]
    model = genai.GenerativeModel(
        model_name='models/gemini-flash-latest',
        system_instruction=system_instruction,
        tools=all_tools
    )
    return model

def _content_to_dict(content: glm.Content) -> Dict[str, Any]:
    parts_list = []
    for part in content.parts:
        part_dict = {}
        if part.text:
            part_dict["text"] = part.text
        elif hasattr(part, 'function_call'):
            part_dict["function_call"] = {
                "name": part.function_call.name,
                "args": dict(part.function_call.args),
            }
        elif hasattr(part, 'function_response'):
            part_dict["function_response"] = {
                "name": part.function_response.name,
                "response": dict(part.function_response.response),
            }
        parts_list.append(part_dict)
    return {"role": content.role, "parts": parts_list}

def processar_turno_do_chat_com_nome_de_usuario(
    history_list: List[Dict[str, Any]], 
    user_prompt: str,
    user_name: str 
) -> (List[Dict[str, Any]], str):
    
    try:
        system_instruction_com_nome = INSTRUCAO_SISTEMA_BASE.replace("[[NOME_DO_USUARIO]]", user_name)
        model = initialize_model(system_instruction_com_nome)

        history_list.append({"role": "user", "parts": [{"text": user_prompt}]})
        response = model.generate_content(history_list)

        if not response.candidates or not response.candidates[0].content.parts:
            return history_list, "A comunicação com a IA falhou (resposta vazia)."

        model_response_content = response.candidates[0].content
        model_response_dict = _content_to_dict(model_response_content)
        part = model_response_dict['parts'][0]
        history_list.append(model_response_dict)

        while "function_call" in part:
            function_call_dict = part["function_call"]
            
            tool_map = {
                "execute_shell_command": execute_shell_command,
                "pesquisar_na_internet": pesquisar_na_internet,
                "analisar_url_e_resumir": analisar_url_e_resumir,
                "gerenciar_notas": gerenciar_notas,
                "agendar_evento": agendar_evento,
                "excluir_evento": excluir_evento,
                "listar_eventos": listar_eventos,
                "ler_arquivo": ler_arquivo,
                "escrever_arquivo": escrever_arquivo,
            }
            
            func_to_call = tool_map.get(function_call_dict["name"])
            
            if not func_to_call:
                result = f"Erro: Função desconhecida '{function_call_dict['name']}'."
            else:
                args = function_call_dict.get("args", {})
                print(f"[ASP] Executando: {function_call_dict['name']}({args})")
                
                try:
                    result = func_to_call(**args)
                except TypeError as e:
                    result = f"Erro de Argumento: A IA tentou chamar {function_call_dict['name']} com argumentos inválidos. {e}"
                except Exception as e:
                    result = f"Erro inesperado na execução da ferramenta: {e}"

            function_response_content = {
                "role": "model",
                "parts": [{
                    "function_response": {
                        "name": function_call_dict["name"],
                        "response": {"output": result}
                    }
                }]
            }
            history_list.append(function_response_content)
            response_2 = model.generate_content(history_list)
            
            if not response_2.candidates: 
                history_list.append({"role": "model", "parts": [{"text": "A comunicação de segunda etapa falhou."}]})
                break

            model_response_content = response_2.candidates[0].content
            model_response_dict = _content_to_dict(model_response_content)
            history_list.append(model_response_dict)
            part = model_response_dict['parts'][0]
            
        final_text_response = part.get("text", "Ocorreu um erro ao processar a resposta da função.")
        return history_list, final_text_response

    except Exception as e:
        print(f"Erro no processar_turno_do_chat: {e}")
        return history_list, f"Perdoe-me, encontrei uma anomalia na comunicação: {e}"