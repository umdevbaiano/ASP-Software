# maia.py (V64 - Lançador do Servidor)
import uvicorn
import sys
import os

# Adiciona a pasta 'src' ao caminho do Python
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

if __name__ == "__main__":
    print("[ASP V64] Iniciando servidor FastAPI em http://127.0.0.1:8000")
    print("Acesse http://127.0.0.1:8000/docs para ver a documentação da API.")
    
    # Uvicorn irá procurar o objeto 'app' dentro do arquivo 'src/api.py'
    # reload=True é excelente para desenvolvimento
    uvicorn.run("api:app", 
                host="127.0.0.1", 
                port=8000, 
                reload=True, 
                app_dir=src_path)