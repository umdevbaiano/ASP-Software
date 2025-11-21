# 🧠 ASP (Maia) - Assistente Pessoal com Agente de IA

Bem-vindo ao repositório do **ASP**! 👋

Este projeto nasceu de uma pergunta simples: **"E se eu pudesse criar um assistente que não apenas conversasse comigo, mas que realmente *fizesse* coisas no meu computador e na nuvem?"**

O resultado é a **Maia**, uma aplicação Full-Stack que une a inteligência do Google Gemini com a capacidade de execução de scripts Python. Não é apenas um chatbot; é um **Agente de IA** capaz de gerenciar minha agenda, pesquisar dados em tempo real e até organizar meus arquivos locais.

## 🚀 O que a Maia faz de verdade?

Eu queria fugir do básico "Olá Mundo" de IA. Por isso, implementei funcionalidades reais usando *Function Calling*:

* **Ela tem "mãos" no meu SO:** A Maia pode executar comandos de shell (com filtros de segurança, claro) e gerenciar arquivos locais.
* **Ela gerencia meu tempo:** Integrei com a API do **Google Calendar** (via OAuth 2.0). Posso dizer *"Agende uma reunião com o Samuel amanhã às 14h"* e ela lida com tudo, inclusive detectando datas relativas como "próxima quinta-feira".
* **Ela vê o mundo:** Diferente de modelos que param no tempo, a Maia usa a **Google Custom Search API** para buscar notícias, cotações e dados em tempo real.
* **Ela tem memória:** Implementei um sistema CRUD local em JSON para que ela possa guardar notas, listas e lembretes que persistem entre sessões.

## 🛠️ Por baixo do capô (Tech Stack)

Este projeto foi um excelente desafio para estruturar uma aplicação moderna e desacoplada:

* **Backend (O Cérebro):** Python com **FastAPI**. Escolhi o FastAPI pela velocidade e pela facilidade em criar endpoints assíncronos. A arquitetura é modular, separando a lógica do agente, autenticação e ferramentas.
* **Frontend (O Rosto):** **Next.js** com TypeScript. Queria algo rápido e reativo.
* **Design:** Usei **Tailwind CSS** para um visual "Dark Mode" limpo e integrei **Three.js (@react-three/fiber)** para dar um toque futurista com elementos 3D no fundo.
* **IA:** Google Generative AI SDK (Gemini 1.5 Flash).

## 📦 Como rodar o projeto

Se você quiser testar a Maia (ou usar o código como base para o seu próprio Jarvis), aqui está o caminho das pedras:

### 1. Clone e Prepare o Backend

```bash
git clone https://github.com/seu-usuario/ASP-Software.git
cd ASP-Software
pip install -r requirements.txt
```

### 2. Configure as Chaves (A parte chata, mas necessária)

Você vai precisar de algumas chaves do Google Cloud. Crie um arquivo `.env` na raiz (usei o `.env.example` como modelo) e preencha:

* `GEMINI_API_KEY`: Para o cérebro.
* `Google Search_API_KEY`: Para ela poder pesquisar na web.
* `Google Search_ENGINE_ID`: O ID do seu mecanismo de busca personalizado.

*Nota: Para o calendário funcionar, você precisará do arquivo `credentials.json` do Google Cloud (OAuth Desktop App) na pasta `/data`.*

### 3. Rode a Mágica

**Backend:**
```bash
python maia.py
```
*O servidor iniciará em `http://127.0.0.1:8000`.*

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
*Acesse `http://localhost:3000` no seu navegador.*

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

## 🚧 Próximos Passos

Este projeto está em evolução constante. Algumas ideias que estou explorando:

- [ ] Implementar um banco de dados real (PostgreSQL) no lugar do JSON.
- [ ] Adicionar login com reconhecimento facial (Biometria).
- [ ] Transformar o módulo de notas em um Habit Tracker completo.

---

Feito com ☕ e Python por **Samuel Miranda**.

## ⚠️ Notas Importantes

  * **Primeiro Uso do Calendário:** Na primeira vez que você pedir para a Maia agendar algo, o terminal do Backend irá gerar um link de autenticação. Você deve clicar no link, autorizar e colar o código de volta no terminal.
  * **Comandos de Sistema:** A Maia tem permissão para executar comandos no seu computador. Embora haja filtros de segurança, use com responsabilidade.

-----

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se livre para contribuir ou utilizar como base para seus próprios assistentes.

-----

**Feito com ☕ e Python por Samuel Miranda.**