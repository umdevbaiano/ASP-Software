"use client";

import { useState, FormEvent, useEffect, useRef } from "react";
import { useParams } from "next/navigation"; 
import ThreeScene from "../../components/ThreeScene"; 

interface HistoryItem {
  role: "user" | "model";
  parts: { text: string }[];
}

const API_URL = "http://127.0.0.1:8000";

export default function ChatPage() {
  const [prompt, setPrompt] = useState<string>("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  const params = useParams();
  const sessionId = params.sessionId as string; 

  useEffect(() => {
    if (sessionId) {
      const fetchHistory = async () => {
        setIsLoading(true);
        try {
          const response = await fetch(`${API_URL}/api/chat/${sessionId}`);
          if (response.ok) {
            const data: HistoryItem[] = await response.json();
            setHistory(data);
          } else {
            setHistory([]); 
          }
        } catch (error) {
          console.error("Falha ao carregar histórico:", error);
        }
        setIsLoading(false);
      };
      fetchHistory();
    }
  }, [sessionId]); 

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading || !sessionId) return;
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
      };

      const response = await fetch(`${API_URL}/api/chat/${sessionId}`, {
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
    <main className="flex h-screen flex-col items-center p-4 md:p-12 text-white font-sans">
      
      <div className="fixed top-0 left-0 w-full h-full -z-10 opacity-30">
        <ThreeScene />
      </div>

      <div className="relative z-10 flex flex-col w-full max-w-2xl h-full">
        <h1 className="text-4xl font-bold mb-2 text-center">ASP (Maia)</h1>
        <p className="text-lg text-gray-400 mb-6 text-center">V92 - Multi-Sessão (Typo Corrigido)</p>

        <div className="flex-grow p-4 bg-gray-800 bg-opacity-80 backdrop-blur-md rounded-lg overflow-y-auto border border-gray-700 mb-4">
          {history.length === 0 && !isLoading && (
            <p className="text-gray-500">
              Sistemas V92 (Multi-Sessão) ativados. Enviando primeiro prompt...
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

        <form onSubmit={handleSubmit} className="w-full flex items-center">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={isLoading ? "Maia está processando..." : "Digite sua mensagem..."}
            disabled={isLoading || !sessionId}
            className="flex-grow p-3 rounded-l-lg bg-gray-700 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading || !sessionId}
            className="p-3 bg-blue-600 rounded-r-lg hover:bg-blue-700 disabled:bg-gray-500"
          >
            {isLoading ? "..." : "Enviar"}
          </button>
        </form>
      </div>
    </main>
  );
}