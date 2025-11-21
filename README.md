# 🧠 ASP (Assistente Pessoal de Software) - Maia

> **Um assistente de I.A. Full-Stack com persistência de dados, integração de calendário e interface 3D.**

O **ASP** é um sistema de assistente virtual inteligente projetado para aumentar a produtividade de desenvolvedores. O núcleo do sistema é a **Maia**, uma personalidade de I.A. (baseada no Google Gemini) capaz de executar tarefas reais no sistema operacional e na nuvem através de *Function Calling* (Chamada de Ferramentas).

Este projeto demonstra uma arquitetura robusta separando um Backend em Python (FastAPI) de um Frontend moderno em Next.js, com foco em **Clean Code**, **Persistência de Dados** e **UX/UI Interativa**.

## ✨ Funcionalidades Principais

### 🧠 Inteligência & Backend (Python/FastAPI)

  * **Cérebro Gemini:** Utiliza o modelo `gemini-1.5-flash` com *System Prompting* avançado para manter uma personalidade consistente (polida, levemente sarcástica e proativa).
  * **Function Calling (Ferramentas Reais):** A I.A. não apenas conversa; ela executa código para:
      * 📅 **Google Calendar:** Agendar, listar e excluir eventos reais (Integração OAuth 2.0).
      * 🔎 **Web Search:** Pesquisar dados em tempo real (cotações, notícias) via Google Custom Search API.
      * 📄 **Análise de Conteúdo:** Ler e resumir artigos técnicos longos via URL scraping.
      * 💻 **Sistema Operacional:** Executar comandos de shell (com filtro de segurança).
      * 💾 **Persistência (CRUD):** Criar e gerenciar listas de notas e tarefas salvas localmente (`JSON`).
  * **API RESTful:** O backend expõe endpoints documentados via Swagger/OpenAPI.

### 🎨 Interface & Frontend (Next.js/React)

  * **Design Moderno:** Interface escura (*Dark Mode*) estilizada com **Tailwind CSS**.
  * **Visualização 3D:** Fundo interativo com elementos 3D renderizados via **Three.js** e **React Three Fiber**.
  * **Efeito Parallax:** Animações suaves de câmera baseadas no scroll usando **Framer Motion**.
  * **Arquitetura de Chat:** Interface reativa com histórico de conversas persistente durante a sessão.

-----

## 🛠️ Tecnologias Utilizadas

  * **Linguagem:** Python 3.11+
  * **Framework Backend:** FastAPI + Uvicorn
  * **I.A.:** Google Generative AI SDK
  * **Frontend:** Next.js 14+, React, TypeScript
  * **Estilização:** Tailwind CSS
  * **3D & Animação:** Three.js, React Three Fiber, Framer Motion
  * **Segurança:** OAuthLib (Google), Python-Dotenv

-----

## 🚀 Instalação e Configuração

Siga os passos abaixo para rodar o projeto localmente.

### Pré-requisitos

  * Python 3.11 ou superior.
  * Node.js 18 ou superior.
  * Conta no Google Cloud Platform (para chaves de API).

### 1\. Configuração do Backend

1.  Clone o repositório:

    ```bash
    git clone https://github.com/seu-usuario/ASP-Software.git
    cd ASP-Software
    ```

2.  Instale as dependências do Python:

    ```bash
    pip install -r requirements.txt
    ```

3.  Configure as Variáveis de Ambiente:

      * Crie um arquivo `.env` na raiz do projeto.
      * Copie o conteúdo de `.env.example` ou adicione as suas chaves:

    <!-- end list -->

    ```ini
    GEMINI_API_KEY="SUA_CHAVE_DO_GEMINI"
    GOOGLE_SEARCH_API_KEY="SUA_CHAVE_CUSTOM_SEARCH"
    GOOGLE_SEARCH_ENGINE_ID="SEU_ID_DE_MECANISMO_CX"
    ```

4.  Configure o Google Calendar (OAuth):

      * Baixe suas credenciais OAuth 2.0 do Google Cloud Console (Tipo: Desktop App).
      * Salve o arquivo como `credentials.json` dentro da pasta `/data` (ou na raiz, dependendo da versão).

### 2\. Configuração do Frontend

1.  Navegue até a pasta do frontend:

    ```bash
    cd frontend
    ```

2.  Instale as dependências do Node:

    ```bash
    npm install
    ```

-----

## ▶️ Como Usar

Você precisará de dois terminais abertos para rodar o sistema Full-Stack.

### Terminal 1: Iniciar o Backend (API)

Na raiz do projeto (`/ASP-Software`), execute:

```bash
python maia.py
```

*O servidor iniciará em `http://127.0.0.1:8000`. Você pode acessar `http://127.0.0.1:8000/docs` para ver a documentação da API.*

### Terminal 2: Iniciar o Frontend (Interface)

Na pasta do frontend (`/ASP-Software/frontend`), execute:

```bash
npm run dev
```

*Acesse `http://localhost:3000` no seu navegador.*

-----

## 📂 Estrutura do Projeto

```
/
├── .env                  # Segredos (NÃO COMMITAR)
├── maia.py               # Lançador do Backend
├── requirements.txt      # Dependências Python
├── data/                 # Persistência (JSONs e Tokens)
├── src/                  # Código Fonte do Backend
│   ├── api.py            # Servidor FastAPI
│   ├── core_agent.py     # Lógica da I.A. (Cérebro)
│   └── tools/            # Ferramentas (Calendar, System, Web, Persistence)
└── frontend/             # Projeto Next.js
    ├── src/app/page.tsx  # Interface de Chat
    └── ...
```

-----

## ⚠️ Notas Importantes

  * **Primeiro Uso do Calendário:** Na primeira vez que você pedir para a Maia agendar algo, o terminal do Backend irá gerar um link de autenticação. Você deve clicar no link, autorizar e colar o código de volta no terminal.
  * **Comandos de Sistema:** A Maia tem permissão para executar comandos no seu computador. Embora haja filtros de segurança, use com responsabilidade.

-----

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se livre para contribuir ou utilizar como base para seus próprios assistentes.

-----

**Desenvolvido por Samuel Miranda**