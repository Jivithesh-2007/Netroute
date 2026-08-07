import React, { useState, useEffect } from 'react';
import { Layers, Shuffle, CheckCircle, AlertTriangle, Cpu, Milestone } from 'lucide-react';

export default function RoutingAlgorithms() {
  const [dfsStack, setDfsStack] = useState<string[]>(['A']);
  const [dfsVisited, setDfsVisited] = useState<string[]>([]);
  const [bfsQueue, setBfsQueue] = useState<string[]>(['A']);
  const [bfsVisited, setBfsVisited] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<'stack-queue' | 'complexities'>('stack-queue');

  // DFS Micro Simulation Loop
  useEffect(() => {
    const dfsGraph: Record<string, string[]> = {
      A: ['B', 'C'],
      B: ['D', 'E'],
      C: ['F'],
      D: [],
      E: [],
      F: []
    };

    let timer = setInterval(() => {
      setDfsStack(prev => {
        if (prev.length === 0) {
          setDfsVisited([]);
          return ['A'];
        }
        const nextStack = [...prev];
        const current = nextStack.pop()!; // Stack POP (LIFO)
        
        setDfsVisited(vis => {
          if (vis.includes(current)) return vis;
          return [...vis, current];
        });

        // Add neighbors to stack
        const neighbors = dfsGraph[current] || [];
        neighbors.forEach(n => {
          if (!nextStack.includes(n)) {
            nextStack.push(n);
          }
        });

        return nextStack;
      });
    }, 2200);

    return () => clearInterval(timer);
  }, []);

  // BFS Micro Simulation Loop
  useEffect(() => {
    const bfsGraph: Record<string, string[]> = {
      A: ['B', 'C'],
      B: ['D', 'E'],
      C: ['F'],
      D: [],
      E: [],
      F: []
    };

    let timer = setInterval(() => {
      setBfsQueue(prev => {
        if (prev.length === 0) {
          setBfsVisited([]);
          return ['A'];
        }
        const nextQueue = [...prev];
        const current = nextQueue.shift()!; // Queue SHIFT (FIFO)

        setBfsVisited(vis => {
          if (vis.includes(current)) return vis;
          return [...vis, current];
        });

        const neighbors = bfsGraph[current] || [];
        neighbors.forEach(n => {
          if (!nextQueue.includes(n)) {
            nextQueue.push(n);
          }
        });

        return nextQueue;
      });
    }, 2200);

    return () => clearInterval(timer);
  }, []);

  return (
    <section id="algorithms" className="py-24 bg-white border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Heading */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider block">
            Algorithm Deep Dive
          </span>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            Routing Traversal Primitives
          </h2>
          <p className="font-sans text-base text-[#0F172A]/70">
            DFS and BFS are the fundamental pillars of graph traversal. Routers use variations of these concepts to establish network state and find paths. Explore their properties below:
          </p>
        </div>

        {/* Two Large Comparison Cards (DFS vs BFS) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start mb-16">
          
          {/* DFS Column */}
          <div className="bg-[#FAFBFC] border border-[#E5E7EB] rounded-2xl p-6.5 sm:p-8 space-y-6 shadow-xs hover:border-[#2563EB]/20 transition-all">
            <div className="flex items-center justify-between border-b border-[#E5E7EB] pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-[#2563EB]/8 flex items-center justify-center text-[#2563EB]">
                  <Layers className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-headings text-xl font-bold text-[#0F172A]">DFS</h3>
                  <span className="font-sans text-xs text-[#2563EB] font-medium uppercase tracking-wider">Depth-First Search</span>
                </div>
              </div>
              <div className="text-right">
                <span className="font-mono text-xs font-semibold bg-[#2563EB]/10 text-[#2563EB] px-2 py-1 rounded">
                  Time: O(V + E)
                </span>
              </div>
            </div>

            {/* working definition */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-[#0F172A] uppercase tracking-wider">Working Principle</span>
              <p className="font-sans text-sm text-[#0F172A]/70 leading-relaxed">
                DFS explores as deep as possible along each branch before backtracking. It uses a <strong>Stack data structure</strong> (either recursion or explicit LIFO storage) to keep track of the path and backward hops.
              </p>
            </div>

            {/* Pros and Cons */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="space-y-3 bg-white border border-[#E5E7EB] p-4 rounded-xl">
                <div className="flex items-center space-x-2 text-[#10B981]">
                  <CheckCircle className="w-4 h-4 shrink-0" />
                  <span className="font-bold text-xs text-[#0F172A] uppercase tracking-wider">Advantages</span>
                </div>
                <ul className="text-xs text-[#0F172A]/70 space-y-1.5 list-disc pl-4 leading-relaxed">
                  <li>Requires less memory space if destination is deep.</li>
                  <li>Saves space compared to BFS on narrow graphs.</li>
                  <li>Excellent for cycle detection and topological sorting.</li>
                </ul>
              </div>

              <div className="space-y-3 bg-white border border-[#E5E7EB] p-4 rounded-xl">
                <div className="flex items-center space-x-2 text-[#F59E0B]">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span className="font-bold text-xs text-[#0F172A] uppercase tracking-wider">Disadvantages</span>
                </div>
                <ul className="text-xs text-[#0F172A]/70 space-y-1.5 list-disc pl-4 leading-relaxed">
                  <li>Does NOT guarantee the shortest path or optimal hop-count.</li>
                  <li>Can get trapped down infinite loops or dead ends.</li>
                </ul>
              </div>
            </div>

            {/* Applications & complexities */}
            <div className="space-y-3 border-t border-[#E5E7EB] pt-4">
              <span className="text-xs font-bold text-[#0F172A] uppercase tracking-wider block">Networking Applications</span>
              <div className="flex flex-wrap gap-2">
                <span className="text-[11px] font-mono bg-white border border-[#E5E7EB] text-[#0F172A]/70 px-2.5 py-1 rounded">Cycle Detection (Spanning Tree)</span>
                <span className="text-[11px] font-mono bg-white border border-[#E5E7EB] text-[#0F172A]/70 px-2.5 py-1 rounded">Topological Dependency Ordering</span>
                <span className="text-[11px] font-mono bg-white border border-[#E5E7EB] text-[#0F172A]/70 px-2.5 py-1 rounded">Connectivity Auditing</span>
              </div>
            </div>

            {/* Micro Simulator stack visualizer */}
            <div className="bg-[#0F172A] text-white p-4.5 rounded-xl space-y-3">
              <div className="flex items-center justify-between text-[11px] text-white/50 border-b border-white/10 pb-2">
                <span>DFS DATA ENGINE: LIFO STACK (ACTIVE)</span>
                <span className="text-amber-400">Current Node: {dfsVisited[dfsVisited.length - 1] || 'None'}</span>
              </div>
              <div className="flex items-center justify-between gap-3 font-mono text-xs">
                <div>
                  <span className="text-white/40 block text-[10px] mb-1">STACK STATE</span>
                  <div className="flex space-x-1.5">
                    {dfsStack.map((item, idx) => (
                      <span key={idx} className="bg-blue-600 text-white px-2 py-1 rounded font-bold border border-blue-400">
                        {item}
                      </span>
                    ))}
                    {dfsStack.length === 0 && <span className="text-white/30">Empty</span>}
                  </div>
                </div>
                <div>
                  <span className="text-white/40 block text-[10px] mb-1">VISITED</span>
                  <div className="flex space-x-1 flex-wrap max-w-[120px] justify-end">
                    {dfsVisited.map((item, idx) => (
                      <span key={idx} className="bg-white/10 text-white/80 px-1 py-0.5 rounded text-[10px]">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* BFS Column */}
          <div className="bg-[#FAFBFC] border border-[#E5E7EB] rounded-2xl p-6.5 sm:p-8 space-y-6 shadow-xs hover:border-[#2563EB]/20 transition-all">
            <div className="flex items-center justify-between border-b border-[#E5E7EB] pb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-[#2563EB]/8 flex items-center justify-center text-[#2563EB]">
                  <Shuffle className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-headings text-xl font-bold text-[#0F172A]">BFS</h3>
                  <span className="font-sans text-xs text-[#2563EB] font-medium uppercase tracking-wider">Breadth-First Search</span>
                </div>
              </div>
              <div className="text-right">
                <span className="font-mono text-xs font-semibold bg-[#2563EB]/10 text-[#2563EB] px-2 py-1 rounded">
                  Time: O(V + E)
                </span>
              </div>
            </div>

            {/* working definition */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-[#0F172A] uppercase tracking-wider">Working Principle</span>
              <p className="font-sans text-sm text-[#0F172A]/70 leading-relaxed">
                BFS explores all immediate neighbor routers first, level by level, before branching deeper. It uses a <strong>Queue data structure</strong> (FIFO - First In First Out) to store neighboring hops, ensuring paths expand uniformly.
              </p>
            </div>

            {/* Pros and Cons */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="space-y-3 bg-white border border-[#E5E7EB] p-4 rounded-xl">
                <div className="flex items-center space-x-2 text-[#10B981]">
                  <CheckCircle className="w-4 h-4 shrink-0" />
                  <span className="font-bold text-xs text-[#0F172A] uppercase tracking-wider">Advantages</span>
                </div>
                <ul className="text-xs text-[#0F172A]/70 space-y-1.5 list-disc pl-4 leading-relaxed">
                  <li>Guarantees the optimal **shortest path** on unweighted graphs.</li>
                  <li>Finds the path with the minimal number of hops.</li>
                  <li>Excellent for local client discovery cascades.</li>
                </ul>
              </div>

              <div className="space-y-3 bg-white border border-[#E5E7EB] p-4 rounded-xl">
                <div className="flex items-center space-x-2 text-[#F59E0B]">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span className="font-bold text-xs text-[#0F172A] uppercase tracking-wider">Disadvantages</span>
                </div>
                <ul className="text-xs text-[#0F172A]/70 space-y-1.5 list-disc pl-4 leading-relaxed">
                  <li>High memory cost O(V) to store all nodes on the frontier.</li>
                  <li>Slow on extremely wide network grids where branches are deep.</li>
                </ul>
              </div>
            </div>

            {/* Applications & complexities */}
            <div className="space-y-3 border-t border-[#E5E7EB] pt-4">
              <span className="text-xs font-bold text-[#0F172A] uppercase tracking-wider block">Networking Applications</span>
              <div className="flex flex-wrap gap-2">
                <span className="text-[11px] font-mono bg-white border border-[#E5E7EB] text-[#0F172A]/70 px-2.5 py-1 rounded">Shortest-Hop Packet Routing (IP routing)</span>
                <span className="text-[11px] font-mono bg-white border border-[#E5E7EB] text-[#0F172A]/70 px-2.5 py-1 rounded">Peer-to-Peer Network Broadcasts</span>
                <span className="text-[11px] font-mono bg-white border border-[#E5E7EB] text-[#0F172A]/70 px-2.5 py-1 rounded">Link-state synchronization</span>
              </div>
            </div>

            {/* Micro Simulator queue visualizer */}
            <div className="bg-[#0F172A] text-white p-4.5 rounded-xl space-y-3">
              <div className="flex items-center justify-between text-[11px] text-white/50 border-b border-white/10 pb-2">
                <span>BFS DATA ENGINE: FIFO QUEUE (ACTIVE)</span>
                <span className="text-cyan-400">Current Node: {bfsVisited[bfsVisited.length - 1] || 'None'}</span>
              </div>
              <div className="flex items-center justify-between gap-3 font-mono text-xs">
                <div>
                  <span className="text-white/40 block text-[10px] mb-1">QUEUE STATE (First-In, First-Out)</span>
                  <div className="flex space-x-1.5">
                    {bfsQueue.map((item, idx) => (
                      <span key={idx} className="bg-sky-600 text-white px-2 py-1 rounded font-bold border border-sky-400">
                        {item}
                      </span>
                    ))}
                    {bfsQueue.length === 0 && <span className="text-white/30">Empty</span>}
                  </div>
                </div>
                <div>
                  <span className="text-white/40 block text-[10px] mb-1">VISITED</span>
                  <div className="flex space-x-1 flex-wrap max-w-[120px] justify-end">
                    {bfsVisited.map((item, idx) => (
                      <span key={idx} className="bg-white/10 text-white/80 px-1 py-0.5 rounded text-[10px]">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
