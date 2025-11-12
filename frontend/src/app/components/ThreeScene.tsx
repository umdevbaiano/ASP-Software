// Arquivo: frontend/src/app/components/ThreeScene.tsx
// (V73 - Correção da Visibilidade do Cubo 3D)

"use client";

import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei'; // NOVO: Importa componentes de 'drei'
import { Mesh } from 'three';

/**
 * Um componente simples para um cubo que gira.
 */
function SpinningBox() {
  const meshRef = useRef<Mesh>(null!);

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += delta * 0.5; // Um pouco mais rápido
      meshRef.current.rotation.y += delta * 0.5;
    }
  });

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[2, 2, 2]} />
      {/* V73: Corrigido o material para ser emissivo e com bordas */}
      <meshBasicMaterial color={"#5865F2"} wireframe={true} /> {/* Agora é um cubo vazado azul */}
    </mesh>
  );
}

/**
 * O componente principal da Cena 3D
 */
export default function ThreeScene() {
  return (
    // V73: Adiciona a cor de fundo ao Canvas e a câmera.
    // O Canvas agora terá um fundo preto sutil (que será invisível devido ao opacity-30 no pai)
    <Canvas style={{ background: '#0a0a0d' }}> {/* Fundo muito escuro para garantir que o Canvas está lá */}
      {/* Câmera V73: Posição inicial para ver o cubo */}
      <PerspectiveCamera makeDefault position={[0, 0, 5]} fov={75} />
      
      {/* Luz ambiente */}
      <ambientLight intensity={0.5} />
      
      {/* Luz pontual */}
      <pointLight position={[10, 10, 10]} intensity={1} />
      
      {/* Nosso cubo giratório */}
      <SpinningBox />
      
      {/* V73: Controles de órbita para poder arrastar e ver o cubo (apenas para depuração) */}
      {/* <OrbitControls /> */} 
    </Canvas>
  );
}