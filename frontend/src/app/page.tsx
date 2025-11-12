// Arquivo: frontend/src/app/page.tsx
// (V75 - Restaurando o estilo do formulário)

"use client";

import { useState, FormEvent, useEffect, useRef } from "react";
import ThreeScene from "./components/ThreeScene"; // (V71)

interface HistoryItem {
  role: "user" | "model";
  parts: { text: string }[];
}

export default function ChatPage() {
  const [prompt, setPrompt] = useState<string>("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const MAIA_API_URL = "http://127.0.0.1:8000/chat";

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    setIsLoading(true);

    const userMessage: HistoryItem = {
      role: "user",
      parts: [{ text: prompt }],
    };
    
    const currentHistory = [...history, userMessage];
    setHistory(currentHistory);
    const currentPrompt = prompt;
    setPrompt(""); 

    try {
      const requestBody = {
        user_prompt: currentPrompt,
        history: history, 
      };

      const response = await fetch(MAIA_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Erro na API: ${response.statusText}`);
      }

      const data = await response.json();
      setHistory(data.updated_history);

    } catch (error) {
      console.error("Falha ao buscar resposta da Maia:", error);
      setHistory([
        ...currentHistory,
        {
          role: "model",
          parts: [{ text: "Desculpe, não consegui me conectar ao backend. O servidor (maia.py) está rodando?" }],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // Fundo V74 (Correto)
    <main className="flex min-h-screen flex-col items-center p-4 md:p-12 text-white font-sans">
      
      {/* Cena 3D V74 (Correto) */}
      <div className="fixed top-0 left-0 w-full h-full -z-10 opacity-30">
        <ThreeScene />
      </div>

      {/* Container do Chat V74 (Correto) */}
      <div className="relative z-10 flex flex-col w-full max-w-2xl h-[85vh]">
        <h1 className="text-4xl font-bold mb-2 text-center">ASP (Maia)</h1>
        <p className="text-lg text-gray-400 mb-6 text-center">V75 - Estilo do Formulário Restaurado</p>

        {/* Área de Exibição do Chat (Correto) */}
        <div className="flex-grow p-4 bg-gray-800 bg-opacity-80 backdrop-blur-md rounded-lg overflow-y-auto border border-gray-700 mb-4">
          {history.length === 0 && (
            <p className="text-gray-500">
              Sistemas V75 (Frontend 3D) ativados. O servidor V66 (Backend) está em execução?
            </p>
          )}

          {history.map((item, index) => (
            <div key={index} className={`mb-3 p-3 rounded-lg max-w-[80%] ${
              item.role === 'user'
                ? 'bg-blue-900 text-right ml-auto'
                : 'bg-gray-700 text-left mr-auto'
            }`}>
              <span className="font-bold capitalize">{item.role === 'model' ? 'Maia' : 'Você'}</span>
              <p className="whitespace-pre-wrap">{item.parts[0].text}</p>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* --- Formulário de Input (V75 - Classes Restauradas) --- */}
        <form onSubmit={handleSubmit} className="w-full flex items-center">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={isLoading ? "Maia está processando..." : "Digite sua mensagem..."}
            disabled={isLoading}
            className="flex-grow p-3 rounded-l-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="p-3 bg-blue-600 rounded-r-lg hover:bg-blue-700 disabled:bg-gray-500"
          >
            {isLoading ? "..." : "Enviar"}
          </button>
        </form>
        {/* --- FIM DA CORREÇÃO V75 --- */}
      </div>
    </main>
  );
}