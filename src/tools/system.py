import os
import subprocess
import platform
import shlex
import re

# (Importa o PROJECT_ROOT do config para a verificação de segurança do escrever_arquivo)
from src.config import PROJECT_ROOT

def execute_shell_command(command: str):
    """Executa um comando de shell (cmd/bash) no sistema operacional."""
    try:
        system_os = platform.system()
        if system_os == "Windows": result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='oem')
        else: result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if not result.stdout and not result.stderr: return "Comando executado com sucesso, sem output."
        output = (result.stdout or "") + (result.stderr or "")
        return f"Sucesso: {output}"
    except subprocess.CalledProcessError as e:
        output = (e.stdout or "") + (e.stderr or "")
        return f"Erro de Execução: O comando '{command}' falhou. Output: {output}"
    except Exception as e: return f"Erro inesperado no sistema: {e}"

def ler_arquivo(caminho_arquivo: str) -> str:
    """Lê o conteúdo de um arquivo de texto no caminho especificado."""
    try:
        if not os.path.exists(caminho_arquivo):
            return f"Erro de Leitura: O arquivo '{caminho_arquivo}' não foi encontrado."
        if os.path.getsize(caminho_arquivo) > 100 * 1024:
            return "Erro de Leitura: O arquivo é muito grande (limite de 100 KB)."
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        print(f"[ASP] Arquivo '{caminho_arquivo}' lido com sucesso.")
        return conteudo
    except Exception as e: return f"Erro inesperado ao tentar ler o arquivo: {e}"

def escrever_arquivo(caminho_arquivo: str, conteudo: str) -> str:
    """Cria ou sobrescreve um arquivo de texto com o conteúdo fornecido."""
    try:
        caminho_absoluto = os.path.abspath(caminho_arquivo)
        caminho_pasta_atual = os.path.abspath(PROJECT_ROOT) # Usa o PROJECT_ROOT
        
        if not caminho_absoluto.startswith(caminho_pasta_atual):
             return "Erro de Escrita: Operação negada. A Maia só pode escrever na pasta do projeto ou subpastas por segurança."
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"[ASP] Arquivo '{caminho_arquivo}' escrito com sucesso.")
        return f"Sucesso: O arquivo '{caminho_arquivo}' foi criado/atualizado."
    except Exception as e: return f"Erro inesperado ao tentar escrever o arquivo: {e}"