// Arquivo: frontend/tailwind.config.ts
// (V76 - Garantindo que o Tailwind leia a pasta 'src/app')

import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    // Assegura que o Tailwind procure por classes (como 'bg-gray-700')
    // nos arquivos dentro de 'src/app/'
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}", // Adicionado por segurança
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;