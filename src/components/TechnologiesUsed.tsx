import React from 'react';
import { Cpu, Smartphone, Code2, Palette, Shield, LayoutGrid, Layers } from 'lucide-react';

export default function TechnologiesUsed() {
  const techStack = [
    {
      name: 'HTML5 Semantic Layouts',
      icon: Code2,
      category: 'Frontend Core',
      desc: 'Enforces clean semantic structures designed for accessible document outlines, utilizing high-contrast labels and proper touch margins.'
    },
    {
      name: 'CSS3 & Tailwind CSS',
      icon: Palette,
      category: 'Design & Layout',
      desc: 'Controls color consistency, mathematical margin variables, responsive layouts, and interactive hover elevation states.'
    },
    {
      name: 'Modern JavaScript (TS)',
      icon: Cpu,
      category: 'Logic Engine',
      desc: 'Powers DFS and BFS algorithms, compiles custom traversal steps, and records execution performance statistics.'
    },
    {
      name: 'Scalable Vector Graphics (SVG)',
      icon: Layers,
      category: 'Vector Visuals',
      desc: 'Renders the live routing topology diagram workspace and individual educational diagrams with crisp pixel-perfect lines.'
    },
    {
      name: 'Graph Traversal (DFS & BFS)',
      icon: Shield,
      category: 'Data Structures',
      desc: 'The foundational data structure traversal algorithms that govern node discovery, path backtracks, and optimal routes.'
    },
    {
      name: 'Networking & IP Protocols',
      icon: LayoutGrid,
      category: 'Protocol Logic',
      desc: 'Provides realistic simulations of IPv4 subnet addresses, packet headers, hops metrics, and TTL decrement regulations.'
    }
  ];

  return (
    <section className="py-24 bg-white border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider block">
            System Stack
          </span>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            Technologies Implemented
          </h2>
          <p className="font-sans text-base text-[#0F172A]/70">
            A modular, client-side educational application built with high performance and responsive design guidelines:
          </p>
        </div>

        {/* Grid Stack */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {techStack.map((tech, idx) => {
            const TechIcon = tech.icon;
            return (
              <div
                key={tech.name}
                className="bg-[#FAFBFC] border border-[#E5E7EB] rounded-2xl p-6 shadow-xs hover:border-[#2563EB]/20 hover:shadow-md transition-all duration-250 flex flex-col justify-between"
                id={`tech-card-${idx}`}
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] bg-white border border-[#E5E7EB] px-2.5 py-1 rounded-md text-[#0F172A]/50 font-bold tracking-wider uppercase font-mono">
                      {tech.category}
                    </span>
                    <TechIcon className="w-4.5 h-4.5 text-[#2563EB]" />
                  </div>
                  
                  <div className="space-y-1.5">
                    <h3 className="font-headings text-base font-extrabold text-[#0F172A]">
                      {tech.name}
                    </h3>
                    <p className="font-sans text-sm text-[#0F172A]/70 leading-relaxed">
                      {tech.desc}
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-[#E5E7EB]/50 mt-4">
                  <span className="text-[10px] font-mono text-[#10B981] font-semibold uppercase tracking-wider">Verified Stable</span>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
