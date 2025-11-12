import sys
import os

# Adiciona a pasta 'src' ao caminho do Python para que possamos importar os módulos
# (Isso garante que o script funcione, não importa de onde você o execute)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

try:
    # Importa o 'cérebro' do nosso código refatorado
    from core_agent import run_chat_loop
except ImportError as e:
    print(f"Erro de Importação: Não foi possível encontrar os módulos em /src/. {e}")
    print("Certifique-se de que as pastas /src/ e /src/tools/ existem e contêm os arquivos .py.")
    exit(1)
except Exception as e:
    print(f"Erro inesperado durante a inicialização: {e}")
    exit(1)

if __name__ == "__main__":
    try:
        # Inicia o loop de chat
        run_chat_loop()
    except KeyboardInterrupt:
        print("\nMaia: Encerrando sessão (Interrupção manual). Tenha um dia produtivo, se possível.")
    except Exception as e:
        print(f"Maia: Oh, desculpe. Ocorreu uma falha crítica no loop principal: {e}")