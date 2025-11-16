// Arquivo: frontend/src/app/components/Sidebar.tsx
// (V91 - O novo componente de navegação)

"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation"; // Hooks de navegação

// API URL (Backend)
const API_URL = "http://127.0.0.1:8000";

interface Session {
  session_id: string;
  title: string;
}

export default function Sidebar() {
  const router = useRouter(); // Para navegar entre chats
  const params = useParams(); // Para saber qual chat está ativo
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Hook para buscar as sessões quando o componente carregar
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await fetch(`${API_URL}/api/sessions/list`);
        if (response.ok) {
          const data: Session[] = await response.json();
          setSessions(data);
          
          // Se não houver chats, cria um. Se houver, carrega o primeiro.
          if (data.length === 0) {
            handleCreateNewChat();
          } else if (!params.sessionId) {
            // Se estiver na home, redireciona para o primeiro chat
            router.push(`/chat/${data[0].session_id}`);
          }
        }
      } catch (error) {
        console.error("Falha ao buscar sessões:", error);
      }
    };
    fetchSessions();
  }, [params.sessionId, router]); // Depende do sessionId

  // Função para criar um novo chat
  const handleCreateNewChat = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/sessions/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "Novo Chat" }),
      });
      const newSession: Session = await response.json();
      
      // Adiciona o novo chat à lista e navega para ele
      setSessions((prevSessions) => [newSession, ...prevSessions]);
      router.push(`/chat/${newSession.session_id}`);
    } catch (error) {
      console.error("Falha ao criar novo chat:", error);
    }
    setIsLoading(false);
  };

  return (
    <nav className="w-64 h-full bg-gray-900 border-r border-gray-700 p-4 flex flex-col">
      <h2 className="text-xl font-bold mb-4">Meus Chats</h2>
      
      <button
        onClick={handleCreateNewChat}
        disabled={isLoading}
        className="w-full p-2 mb-4 bg-blue-600 rounded hover:bg-blue-700 disabled:bg-gray-500"
      >
        {isLoading ? "Criando..." : "+ Novo Chat"}
      </button>

      {/* Lista de Chats (Scroll) */}
      <div className="flex-grow overflow-y-auto">
        {sessions.map((session) => (
          <a
            key={session.session_id}
            href={`/chat/${session.session_id}`}
            // Destaca o chat que está ativo (baseado no URL)
            className={`block p-2 rounded truncate ${
              params.sessionId === session.session_id
                ? 'bg-gray-700'
                : 'hover:bg-gray-800'
            }`}
          >
            {session.title}
          </a>
        ))}
      </div>
    </nav>
  );
}