// Arquivo: frontend/src/app/layout.tsx
// (V80/V81 - Aplicando classes de fundo no layout)

import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css"; // Esta linha importa o V80 (globals.css)

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ASP (Maia) Frontend",
  description: "Interface para o Assistente Pessoal de Software",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-br">
      {/*
        CORREÇÃO V80/V81:
        As classes de fundo ('bg-gray-950') e texto ('text-white')
        são aplicadas aqui.
      */}
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-950 text-white`}
      >
        {children}
      </body>
    </html>
  );
}