import google.generativeai as genai
from google.ai import generativelanguage as glm
import os

# Importa a configuração (chaves) e a "Alma"
from src.config import GEMINI_API_KEY, PROJECT_ROOT
from src.system_prompt import INSTRUCAO_SISTEMA # (Vamos criar este arquivo)

# Importa TODAS as ferramentas dos módulos
from src.tools.system import execute_shell_command, ler_arquivo, escrever_arquivo
from src.tools.persistence import gerenciar_notas
from src.tools.web import pesquisar_na_internet, analisar_url_e_resumir
from src.tools.calendar import agendar_evento, excluir_evento, listar_eventos

# --- Configuração do Agente ---
def initialize_model():
    """Configura e retorna o modelo GenerativeModel com todas as ferramentas."""
    
    # Configura a chave do Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Lista de todas as funções que a Maia pode chamar
    all_tools = [
        execute_shell_command, pesquisar_na_internet, agendar_evento, 
        excluir_evento, listar_eventos, ler_arquivo, escrever_arquivo, 
        analisar_url_e_resumir, gerenciar_notas
    ]
    
    model = genai.GenerativeModel(
        model_name='models/gemini-flash-latest',
        system_instruction=INSTRUCAO_SISTEMA,
        tools=all_tools
    )
    return model

def run_chat_loop():
    """Inicia e gerencia o loop de chat principal com o usuário."""
    
    model = initialize_model()
    history = []
    
    # Define os caminhos dos arquivos de autenticação relativos à raiz do projeto
    os.chdir(PROJECT_ROOT) 

    print("Maia: Sistemas V61 (Refatorados) ativados. Otimização de persistência (CRUD) concluída. No que posso dedicar minha capacidade de processamento neste momento?")

    while True:
        try:
            prompt_usuario = input("Você: ")

            if prompt_usuario.lower() == 'sair':
                print("Maia: Encerrando sessão. Tenha um dia produtivo, se possível.")
                break
            if not prompt_usuario:
                user_content = glm.Content(parts=[glm.Part(text="O usuário não disse nada. O histórico está vazio ou a última ação não sugere um próximo passo lógico. Seja proativa e sugira o próximo passo mais eficiente com seu tom polido e superior, mencionando as ferramentas, e com base no HISTÓRICO da conversa.")], role="user")
                history.append(user_content)
            else:
                user_content = glm.Content(parts=[glm.Part(text=prompt_usuario)], role="user")
                history.append(user_content)
            
            response = model.generate_content(history)
            
            if not response.candidates or not response.candidates[0].content.parts:
                print("Maia: A comunicação com a IA falhou. (O servidor do Gemini devolveu uma resposta vazia). Verifique a chave de API.")
                continue

            model_response_content = response.candidates[0].content
            part = model_response_content.parts[0]
            history.append(model_response_content)
            
            # --- Loop de Função (O "Agente") ---
            while part.function_call:
                function_call = part.function_call
                
                # Mapeia o nome da função (string) para a função Python real
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
                
                func_to_call = tool_map.get(function_call.name)
                
                if not func_to_call:
                    result = f"Erro: Função desconhecida '{function_call.name}'."
                else:
                    # Extrai os argumentos que a IA enviou
                    args = {key: value for key, value in function_call.args.items()}
                    print(f"[ASP] Executando: {function_call.name}({args})")
                    
                    try:
                        # Executa a função Python com os argumentos
                        result = func_to_call(**args)
                    except TypeError as e:
                        result = f"Erro de Argumento: A IA tentou chamar {function_call.name} com argumentos inválidos. {e}"
                    except Exception as e:
                        result = f"Erro inesperado na execução da ferramenta: {e}"

                # Envia o resultado de volta para a IA
                function_response_part = glm.Part(function_response=glm.FunctionResponse(
                        name=function_call.name,
                        response={"output": result}
                ))
                function_response_content = glm.Content(parts=[function_response_part], role="model")
                history.append(function_response_content)
                
                # Pede a próxima resposta (que deve ser texto)
                response_2 = model.generate_content(history)
                
                if not response_2.candidates: 
                    print("Maia: A comunicação de segunda etapa falhou.")
                    break

                model_response_content = response_2.candidates[0].content
                history.append(model_response_content)
                part = model_response_content.parts[0]
                
            final_text_response = part.text
            print(f"Maia: {final_text_response}\n")

        except Exception as e:
            print(f"Maia: Perdoe-me, encontrei uma anomalia na comunicação: {e}")
            break