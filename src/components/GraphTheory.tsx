import React, { useState } from 'react';
import { Circle, Hash, ArrowRightLeft, Table, List, Landmark, HelpCircle } from 'lucide-react';

interface TheoryItem {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  definition: string;
  networkingAnalogy: string;
}

export default function GraphTheory() {
  const [selectedConcept, setSelectedConcept] = useState<string>('vertices');

  const concepts: TheoryItem[] = [
    {
      id: 'vertices',
      title: 'Vertices (V)',
      icon: Circle,
      definition: 'The fundamental points of a graph. In routing, a vertex (or node) represents an individual router, switch, or host system capable of packet processing.',
      networkingAnalogy: 'Analogy: An edge router or core server in a datacenter.'
    },
    {
      id: 'edges',
      title: 'Edges (E)',
      icon: Hash,
      definition: 'The lines connecting vertices. An edge represents a physical or logical communication link between routers over which packet streams propagate.',
      networkingAnalogy: 'Analogy: Fiber-optic lines, coaxial lines, or wireless radio channels.'
    },
    {
      id: 'weighted',
      title: 'Weighted Graph',
      icon: Landmark,
      definition: 'A graph where each edge has a numerical value (weight). In network routing, weights are assigned to calculate latency, link quality, or available bandwidth.',
      networkingAnalogy: 'Analogy: High-bandwidth fibers have cost = 1; congested copper lines have cost = 10.'
    },
    {
      id: 'directed',
      title: 'Directed vs Undirected',
      icon: ArrowRightLeft,
      definition: 'Directed graphs restrict traversal to one direction. Undirected graphs permit bidirectional travel. Most physical internet routers support bidirectional routing.',
      networkingAnalogy: 'Analogy: A simplex optical channel (directed) vs duplex Ethernet cable (undirected).'
    },
    {
      id: 'matrix',
      title: 'Adjacency Matrix',
      icon: Table,
      definition: 'A 2D square matrix where cells represent edge weights. Useful for dense networks but uses O(V²) space complexity, representing infinite cost if not connected.',
      networkingAnalogy: 'Analogy: A central routing registry database indexing every single router pair.'
    },
    {
      id: 'list',
      title: 'Adjacency List',
      icon: List,
      definition: 'A collection of lists representing neighbor collections for each vertex. Highly space-efficient O(V+E) for sparse graphs, which is the default in router design.',
      networkingAnalogy: 'Analogy: A router’s local neighbor discovery table (CDP/LLDP cache).'
    }
  ];

  // Renders the specific interactive SVG based on chosen concept
  const renderSvgDiagram = () => {
    switch (selectedConcept) {
      case 'vertices':
        return (
          <svg viewBox="0 0 400 300" className="w-full h-full max-h-[300px]">
            {/* Draw nodes */}
            <circle cx="100" cy="150" r="16" fill="#2563EB" fillOpacity="0.1" stroke="#2563EB" strokeWidth="2" strokeDasharray="4 2" />
            <circle cx="100" cy="150" r="8" fill="#2563EB" />
            <text x="100" y="190" fontSize="12" fontWeight="600" fill="#0F172A" textAnchor="middle" fontFamily="Space Grotesk">Vertex A</text>

            <circle cx="300" cy="150" r="16" fill="#2563EB" fillOpacity="0.1" stroke="#2563EB" strokeWidth="2" strokeDasharray="4 2" />
            <circle cx="300" cy="150" r="8" fill="#2563EB" />
            <text x="300" y="190" fontSize="12" fontWeight="600" fill="#0F172A" textAnchor="middle" fontFamily="Space Grotesk">Vertex B</text>

            <circle cx="200" cy="80" r="8" fill="#475569" />
            <text x="200" y="110" fontSize="11" fill="#475569" textAnchor="middle" fontFamily="Inter">Vertex C (Router)</text>

            {/* Info overlays */}
            <rect x="130" y="220" width="140" height="30" rx="6" fill="#0F172A" />
            <text x="200" y="239" fontSize="11" fill="#FFFFFF" textAnchor="middle" fontFamily="monospace">V = &#123;A, B, C&#125;</text>
          </svg>
        );
      case 'edges':
        return (
          <svg viewBox="0 0 400 300" className="w-full h-full max-h-[300px]">
            <line x1="100" y1="150" x2="300" y2="150" stroke="#2563EB" strokeWidth="3" />
            <circle cx="100" cy="150" r="8" fill="#0F172A" />
            <circle cx="300" cy="150" r="8" fill="#0F172A" />
            <text x="100" y="130" fontSize="11" fill="#0F172A" textAnchor="middle" fontFamily="Inter">Node A</text>
            <text x="300" y="130" fontSize="11" fill="#0F172A" textAnchor="middle" fontFamily="Inter">Node B</text>

            <rect x="170" y="160" width="60" height="20" rx="4" fill="#38BDF8" />
            <text x="200" y="174" fontSize="10" fontWeight="bold" fill="#0F172A" textAnchor="middle" fontFamily="Inter">Link (Edge)</text>

            <rect x="130" y="220" width="140" height="30" rx="6" fill="#0F172A" />
            <text x="200" y="239" fontSize="11" fill="#FFFFFF" textAnchor="middle" fontFamily="monospace">E = &#123;(A, B)&#125;</text>
          </svg>
        );
      case 'weighted':
        return (
          <svg viewBox="0 0 400 300" className="w-full h-full max-h-[300px]">
            {/* Top link */}
            <path d="M 100 150 Q 200 80 300 150" fill="none" stroke="#E5E7EB" strokeWidth="2" />
            {/* Bottom link */}
            <path d="M 100 150 Q 200 220 300 150" fill="none" stroke="#2563EB" strokeWidth="3" />

            <circle cx="100" cy="150" r="8" fill="#0F172A" />
            <circle cx="300" cy="150" r="8" fill="#0F172A" />

            {/* Weights */}
            <rect x="185" y="80" width="30" height="20" rx="4" fill="#FFFFFF" stroke="#E5E7EB" strokeWidth="1" />
            <text x="200" y="94" fontSize="11" fontWeight="bold" fill="#0F172A" textAnchor="middle" fontFamily="monospace">w=10</text>

            <rect x="185" y="180" width="30" height="20" rx="4" fill="#2563EB" />
            <text x="200" y="194" fontSize="11" fontWeight="bold" fill="#FFFFFF" textAnchor="middle" fontFamily="monospace">w=2</text>

            <text x="200" y="245" fontSize="11" fill="#475569" textAnchor="middle" fontFamily="Inter">Selected Path: Bottom Link (Weight = 2)</text>
          </svg>
        );
      case 'directed':
        return (
          <svg viewBox="0 0 400 300" className="w-full h-full max-h-[300px]">
            {/* Arrow Marker Definitions */}
            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563EB" />
              </marker>
              <marker id="arrow-gray" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#94A3B8" />
              </marker>
            </defs>

            {/* Directed link */}
            <line x1="80" y1="110" x2="200" y2="110" stroke="#2563EB" strokeWidth="2.5" markerEnd="url(#arrow)" />
            <text x="140" y="95" fontSize="10" fill="#2563EB" fontWeight="bold" textAnchor="middle" fontFamily="monospace">Directed (One-way)</text>

            {/* Undirected link */}
            <line x1="80" y1="200" x2="200" y2="200" stroke="#94A3B8" strokeWidth="2.5" markerEnd="url(#arrow-gray)" markerStart="url(#arrow-gray)" />
            <text x="140" y="185" fontSize="10" fill="#475569" fontWeight="bold" textAnchor="middle" fontFamily="monospace">Undirected (Two-way)</text>

            <circle cx="80" cy="110" r="7" fill="#0F172A" />
            <circle cx="200" cy="110" r="7" fill="#0F172A" />

            <circle cx="80" cy="200" r="7" fill="#0F172A" />
            <circle cx="200" cy="200" r="7" fill="#0F172A" />

            <text x="310" y="115" fontSize="11" fill="#475569" width="100" fontFamily="Inter">A → B Only</text>
            <text x="310" y="205" fontSize="11" fill="#475569" width="100" fontFamily="Inter">A ↔ B Duplex</text>
          </svg>
        );
      case 'matrix':
        return (
          <div className="flex flex-col h-full justify-center items-center font-mono text-xs bg-[#0F172A] text-white p-6 rounded-xl border border-[#E5E7EB]">
            <span className="text-[#38BDF8] mb-3 self-start text-[10px] tracking-wider font-semibold uppercase">Adjacency Cost Matrix</span>
            <div className="grid grid-cols-5 gap-3 text-center border-b border-white/10 pb-2 w-full font-bold">
              <span className="text-white/40"></span>
              <span className="text-white">A</span>
              <span className="text-white">B</span>
              <span className="text-white">C</span>
              <span className="text-white">D</span>
            </div>
            <div className="grid grid-cols-5 gap-3 text-center py-2 w-full">
              <span className="font-bold text-white/50 text-left">A</span>
              <span className="text-white/30">0</span>
              <span className="text-emerald-400 font-bold">4</span>
              <span className="text-emerald-400 font-bold">8</span>
              <span className="text-white/30">∞</span>
            </div>
            <div className="grid grid-cols-5 gap-3 text-center py-2 w-full">
              <span className="font-bold text-white/50 text-left">B</span>
              <span className="text-emerald-400 font-bold">4</span>
              <span className="text-white/30">0</span>
              <span className="text-white/30">∞</span>
              <span className="text-emerald-400 font-bold">2</span>
            </div>
            <div className="grid grid-cols-5 gap-3 text-center py-2 w-full">
              <span className="font-bold text-white/50 text-left">C</span>
              <span className="text-emerald-400 font-bold">8</span>
              <span className="text-white/30">∞</span>
              <span className="text-white/30">0</span>
              <span className="text-emerald-400 font-bold">5</span>
            </div>
            <div className="grid grid-cols-5 gap-3 text-center pt-2 w-full border-t border-white/10">
              <span className="font-bold text-white/50 text-left">D</span>
              <span className="text-white/30">∞</span>
              <span className="text-emerald-400 font-bold">2</span>
              <span className="text-emerald-400 font-bold">5</span>
              <span className="text-white/30">0</span>
            </div>
          </div>
        );
      case 'list':
        return (
          <div className="flex flex-col h-full justify-center font-mono text-xs bg-white text-[#0F172A] p-6 rounded-xl border border-[#E5E7EB] space-y-4">
            <span className="text-[#2563EB] text-[10px] tracking-wider font-semibold uppercase">Adjacency Neighbor Lists</span>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <span className="bg-[#0F172A] text-white px-2 py-0.5 rounded font-bold">A</span>
                <span className="text-gray-400">→</span>
                <span className="bg-[#2563EB]/5 border border-[#2563EB]/15 px-2 py-0.5 rounded text-[#2563EB] font-bold">B (cost: 4)</span>
                <span className="text-gray-400">→</span>
                <span className="bg-[#2563EB]/5 border border-[#2563EB]/15 px-2 py-0.5 rounded text-[#2563EB] font-bold">C (cost: 8)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="bg-[#0F172A] text-white px-2 py-0.5 rounded font-bold">B</span>
                <span className="text-gray-400">→</span>
                <span className="bg-[#2563EB]/5 border border-[#2563EB]/15 px-2 py-0.5 rounded text-[#2563EB] font-bold">A (cost: 4)</span>
                <span className="text-gray-400">→</span>
                <span className="bg-[#2563EB]/5 border border-[#2563EB]/15 px-2 py-0.5 rounded text-[#2563EB] font-bold">D (cost: 2)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="bg-[#0F172A] text-white px-2 py-0.5 rounded font-bold">C</span>
                <span className="text-gray-400">→</span>
                <span className="bg-[#2563EB]/5 border border-[#2563EB]/15 px-2 py-0.5 rounded text-[#2563EB] font-bold">A (cost: 8)</span>
                <span className="text-gray-400">→</span>
                <span className="bg-[#2563EB]/5 border border-[#2563EB]/15 px-2 py-0.5 rounded text-[#2563EB] font-bold">D (cost: 5)</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="bg-[#0F172A] text-white px-2 py-0.5 rounded font-bold">D</span>
                <span className="text-gray-400">→</span>
                <span className="bg-[#2563EB]/5 border border-[#2563EB]/15 px-2 py-0.5 rounded text-[#2563EB] font-bold">B (cost: 2)</span>
                <span className="text-gray-400">→</span>
                <span className="bg-[#2563EB]/5 border border-[#2563EB]/15 px-2 py-0.5 rounded text-[#2563EB] font-bold">C (cost: 5)</span>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <section id="graph-theory" className="py-24 bg-[#FAFBFC] border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider block">
            Mathematical Foundation
          </span>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            Graph Theory in Network Routing
          </h2>
          <p className="font-sans text-base sm:text-lg text-[#0F172A]/70">
            Before applying routing algorithms, we represent the physical telecommunications topology using core graph structures. Learn how graph primitives model complex optical networks:
          </p>
        </div>

        {/* Master-Detail Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          
          {/* Concept Navigation Links (Left) */}
          <div className="lg:col-span-7 flex flex-col space-y-3 justify-center">
            {concepts.map((concept) => {
              const ConceptIcon = concept.icon;
              const isSelected = selectedConcept === concept.id;
              
              return (
                <button
                  key={concept.id}
                  onClick={() => setSelectedConcept(concept.id)}
                  className={`text-left p-4.5 rounded-xl border transition-all duration-200 cursor-pointer flex items-start space-x-4 ${
                    isSelected
                      ? 'bg-white border-[#2563EB] shadow-xs'
                      : 'bg-white/40 border-[#E5E7EB] hover:border-[#2563EB]/30'
                  }`}
                  id={`theory-nav-${concept.id}`}
                >
                  <div className={`w-10 h-10 rounded-lg shrink-0 flex items-center justify-center transition-colors ${
                    isSelected ? 'bg-[#2563EB] text-white' : 'bg-white border border-[#E5E7EB] text-[#0F172A]/60'
                  }`}>
                    <ConceptIcon className="w-5 h-5" />
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-headings text-base font-bold text-[#0F172A]">
                        {concept.title}
                      </span>
                      {isSelected && (
                        <span className="text-[10px] bg-[#2563EB]/8 text-[#2563EB] font-semibold px-1.5 py-0.5 rounded uppercase tracking-wider">
                          Selected Model
                        </span>
                      )}
                    </div>
                    <p className="font-sans text-sm text-[#0F172A]/70 leading-relaxed">
                      {concept.definition}
                    </p>
                    <p className="font-sans text-xs text-[#2563EB] font-medium pt-1.5">
                      {concept.networkingAnalogy}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Diagram Preview Area (Right) */}
          <div className="lg:col-span-5 flex flex-col">
            <div className="bg-white border border-[#E5E7EB] rounded-2xl p-6.5 shadow-xs flex flex-col justify-between h-full min-h-[350px]">
              
              <div className="flex items-center justify-between border-b border-[#E5E7EB] pb-3.5">
                <span className="text-xs font-bold text-[#0F172A] tracking-wide uppercase">
                  Diagram / Matrix Model
                </span>
                <span className="inline-flex items-center space-x-1.5 text-xs text-[#0F172A]/50">
                  <HelpCircle className="w-3.5 h-3.5 text-[#2563EB]" />
                  <span>Click concepts on left to switch</span>
                </span>
              </div>

              {/* Centered Render */}
              <div className="flex-1 flex items-center justify-center py-6">
                <div className="w-full max-w-[340px]">
                  {renderSvgDiagram()}
                </div>
              </div>

              {/* Sub-label */}
              <div className="bg-[#FAFBFC] border border-[#E5E7EB] rounded-xl p-3.5 text-center">
                <span className="font-mono text-xs text-[#0F172A]/60 block">
                  Interactive topology node models conform to RFC-1122 specifications.
                </span>
              </div>

            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
