import uvicorn
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir) 

if __name__ == "__main__":
    print("[ASP V96] Iniciando servidor FastAPI em http://127.0.0.1:8000")
    print("Acesse http://127.0.0.1:8000/docs para ver a documentação da API.")
    
    uvicorn.run("src.api:app", 
                host="127.0.0.1", 
                port=8000, 
                reload=True)