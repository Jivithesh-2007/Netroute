import React, { useEffect, useRef, useState } from 'react';
import { ArrowRight, Server, Shield, Network, Zap } from 'lucide-react';

export default function Hero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Stats in Hero for counters
  const [activePackets, setActivePackets] = useState(12);
  const [throughput, setThroughput] = useState(148.5);

  useEffect(() => {
    // Canvas animation for background topology with moving packets
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = canvas.width = canvas.offsetWidth;
    let height = canvas.height = canvas.offsetHeight;

    const handleResize = () => {
      if (canvas) {
        width = canvas.width = canvas.offsetWidth;
        height = canvas.height = canvas.offsetHeight;
      }
    };
    window.addEventListener('resize', handleResize);

    // Create stable network topology
    const numNodes = 12;
    const nodes: { x: number; y: number; radius: number; color: string; label: string; speed: number; angle: number }[] = [];
    
    // Distribute nodes across canvas
    for (let i = 0; i < numNodes; i++) {
      // Columns distribution for logical flow (left to right)
      const col = i % 4;
      const row = Math.floor(i / 4);
      const xOffset = (width / 5) * (col + 1) + (Math.random() * 40 - 20);
      const yOffset = (height / 4) * (row + 1) + (Math.random() * 40 - 20);

      nodes.push({
        x: xOffset,
        y: yOffset,
        radius: 5 + Math.random() * 3,
        color: i === 0 || i === numNodes - 1 ? '#2563EB' : '#475569',
        label: i === 0 ? 'Gateway' : i === numNodes - 1 ? 'Terminal B' : `Router ${i}`,
        speed: 0.1 + Math.random() * 0.2,
        angle: Math.random() * Math.PI * 2,
      });
    }

    // Connect nodes based on proximity (creating edges)
    const edges: { source: number; target: number; weight: number }[] = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        // Connect nodes that are within reasonable distance to create a grid/network topology
        if (dist < width / 3.5 && edges.filter(e => e.source === i).length < 3) {
          edges.push({ source: i, target: j, weight: Math.floor(dist / 50) });
        }
      }
    }

    // Generate active travelling packets along edges
    const packets: { edgeIndex: number; progress: number; speed: number; size: number; reverse: boolean }[] = [];
    const maxPackets = 16;
    for (let i = 0; i < maxPackets; i++) {
      packets.push({
        edgeIndex: Math.floor(Math.random() * edges.length),
        progress: Math.random(),
        speed: 0.005 + Math.random() * 0.01,
        size: 3 + Math.random() * 2,
        reverse: Math.random() > 0.5,
      });
    }

    // Animation Loop
    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // 1. Draw Edges
      ctx.lineWidth = 1.2;
      edges.forEach(edge => {
        const sourceNode = nodes[edge.source];
        const targetNode = nodes[edge.target];
        
        ctx.strokeStyle = 'rgba(229, 231, 235, 0.5)'; // Subtle border color
        ctx.beginPath();
        ctx.moveTo(sourceNode.x, sourceNode.y);
        ctx.lineTo(targetNode.x, targetNode.y);
        ctx.stroke();
      });

      // 2. Draw Packet Pulses traveling along Edges
      packets.forEach(p => {
        if (p.edgeIndex >= edges.length) return;
        const edge = edges[p.edgeIndex];
        const sourceNode = nodes[edge.source];
        const targetNode = nodes[edge.target];

        // Linear interpolation for packet coordinates
        const start = p.reverse ? targetNode : sourceNode;
        const end = p.reverse ? sourceNode : targetNode;

        const x = start.x + (end.x - start.x) * p.progress;
        const y = start.y + (end.y - start.y) * p.progress;

        // Packet glow/halo
        ctx.beginPath();
        ctx.arc(x, y, p.size * 2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(56, 189, 248, 0.25)'; // Accent color #38BDF8
        ctx.fill();

        // Main packet dot
        ctx.beginPath();
        ctx.arc(x, y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = '#2563EB'; // Primary color
        ctx.fill();

        // Advance progress
        p.progress += p.speed;
        if (p.progress >= 1) {
          p.progress = 0;
          // Randomly switch to a connecting edge
          const currentTargetId = p.reverse ? edge.source : edge.target;
          const connectingEdges = edges.map((e, idx) => ({ e, idx })).filter(item => 
            item.e.source === currentTargetId || item.e.target === currentTargetId
          );
          if (connectingEdges.length > 0) {
            const next = connectingEdges[Math.floor(Math.random() * connectingEdges.length)];
            p.edgeIndex = next.idx;
            p.reverse = next.e.source !== currentTargetId;
          } else {
            p.edgeIndex = Math.floor(Math.random() * edges.length);
          }
        }
      });

      // 3. Draw Nodes with subtle pulses
      nodes.forEach((node, idx) => {
        // Node pulse halo
        const pulse = Math.sin(Date.now() * 0.003 + idx) * 4;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + pulse + 2, 0, Math.PI * 2);
        ctx.fillStyle = idx === 0 || idx === numNodes - 1 
          ? 'rgba(37, 99, 235, 0.08)' 
          : 'rgba(71, 85, 105, 0.05)';
        ctx.fill();

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fillStyle = node.color;
        ctx.fill();

        // Node outline
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Labels for gateways
        if (idx === 0 || idx === numNodes - 1) {
          ctx.font = '600 11px Inter, sans-serif';
          ctx.fillStyle = '#0F172A';
          ctx.textAlign = 'center';
          ctx.fillText(node.label, node.x, node.y - 14);
        }
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    // Randomize stats counters subtly
    const interval = setInterval(() => {
      setActivePackets(prev => Math.max(8, Math.min(20, prev + (Math.random() > 0.5 ? 1 : -1))));
      setThroughput(prev => parseFloat(Math.max(130.0, Math.min(165.0, prev + (Math.random() * 4 - 2))).toFixed(1)));
    }, 3000);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      clearInterval(interval);
    };
  }, []);

  const handleScrollTo = (id: string) => {
    const element = document.querySelector(id);
    if (element) {
      const offset = 80;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <section
      id="hero"
      ref={containerRef}
      className="relative min-h-screen pt-28 pb-16 flex items-center overflow-hidden bg-[#FAFBFC]"
    >
      {/* Topology Canvas Background */}
      <div className="absolute inset-0 z-0">
        <canvas ref={canvasRef} className="w-full h-full opacity-65" />
      </div>

      {/* Decorative Light Radial Gradients (Subtle design touch, not flashy) */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-radial from-[#38BDF8]/5 to-transparent blur-3xl pointer-events-none z-0" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Main Copy */}
          <div className="lg:col-span-7 space-y-8 text-left">
            
            {/* Project Pill - IBM Style */}
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-50 text-[#2563EB] rounded-full text-xs font-bold mb-6 animate-fade-in">
              <span className="w-1.5 h-1.5 rounded-full bg-[#2563EB]" />
              <span className="text-xs font-extrabold tracking-wider uppercase">
                INDUSTRY-LEVEL MICRO PROJECT 06
              </span>
            </div>

            {/* Title */}
            <div className="space-y-4">
              <h1 className="font-headings text-5xl sm:text-6xl font-extrabold tracking-tight text-[#0F172A] leading-[1.1]">
                Network Packet <br className="hidden sm:inline" />
                <span className="text-[#2563EB]">Routing Simulator</span>
              </h1>
              
              <p className="font-headings text-lg sm:text-xl font-bold text-[#0F172A]/80 leading-relaxed max-w-xl">
                Graph-Based Routing Algorithms for Efficient Network Packet Transmission
              </p>
            </div>

            {/* Description Paragraphs explaining routing */}
            <div className="text-base text-[#0F172A]/70 space-y-4 max-w-xl font-sans leading-relaxed">
              <p>
                In telecommunication networks, <strong>Packet Routing</strong> is the core mechanism of selecting optimal paths for data packets to traverse from a source system to a destination across interconnected router nodes.
              </p>
              <p>
                By representing a network topology as a mathematical graph where routers are <strong>vertices</strong> and communication channels are <strong>weighted edges</strong>, graph-traversal algorithms like Depth-First Search (DFS) and Breadth-First Search (BFS) enable deterministic routing, minimum-hop analysis, and robust failover modeling.
              </p>
            </div>

            {/* Buttons with hover states and icons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-2">
              <button
                onClick={() => handleScrollTo('#simulator')}
                className="inline-flex items-center justify-center space-x-2.5 bg-[#2563EB] text-white px-6 py-3 rounded-xl font-extrabold text-sm shadow-md shadow-blue-200 hover:bg-[#0F172A] hover:shadow-lg transition-all duration-200 cursor-pointer active:scale-98"
              >
                <span>Live Simulation</span>
                <ArrowRight className="w-4.5 h-4.5" />
              </button>
              <button
                onClick={() => handleScrollTo('#algorithms')}
                className="inline-flex items-center justify-center space-x-2 bg-white text-[#0F172A] px-6 py-3 rounded-xl font-extrabold text-sm border border-[#E5E7EB] shadow-xs hover:border-[#2563EB] hover:bg-[#FAFBFC] transition-all duration-200 cursor-pointer"
              >
                <span>Explore Algorithms</span>
              </button>
            </div>
          </div>

          {/* Interactive Metric Showcase Box - Cisco / Microsoft Learn inspired (Glassmorphism inside Hero) */}
          <div className="lg:col-span-5 relative">
            <div className="relative bg-white/75 backdrop-blur-md border border-[#E5E7EB] rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
              
              <div className="flex items-center justify-between border-b border-[#E5E7EB] pb-4">
                <div className="flex items-center space-x-2.5">
                  <div className="w-8 h-8 rounded-lg bg-[#2563EB]/10 flex items-center justify-center text-[#2563EB]">
                    <Zap className="w-4.5 h-4.5" />
                  </div>
                  <span className="font-semibold text-sm text-[#0F172A]">Network Status Board</span>
                </div>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-[#10B981]/10 text-[#10B981]">
                  Live Visualizer Active
                </span>
              </div>

              {/* Grid Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-[#FAFBFC] p-4 rounded-xl border border-[#E5E7EB] hover:border-[#2563EB]/40 transition-colors">
                  <span className="block text-xs font-medium text-[#0F172A]/50 uppercase tracking-wider mb-1">
                    Simulated Packets
                  </span>
                  <span className="text-2xl font-extrabold text-[#0F172A] font-headings tracking-tight">
                    {activePackets} <span className="text-xs font-normal text-[#0F172A]/60">active</span>
                  </span>
                </div>
                
                <div className="bg-[#FAFBFC] p-4 rounded-xl border border-[#E5E7EB] hover:border-[#2563EB]/40 transition-colors">
                  <span className="block text-xs font-medium text-[#0F172A]/50 uppercase tracking-wider mb-1">
                    Simulation Latency
                  </span>
                  <span className="text-2xl font-extrabold text-[#0F172A] font-headings tracking-tight">
                    {throughput} <span className="text-xs font-normal text-[#0F172A]/60">ms</span>
                  </span>
                </div>
              </div>

              {/* Visualized Packet Payload Header Example */}
              <div className="bg-[#0F172A] text-white p-4 rounded-xl space-y-2.5 font-mono text-xs">
                <div className="flex items-center justify-between border-b border-white/10 pb-1.5 text-white/50">
                  <span>PACKET HEADER (IPV4)</span>
                  <span className="text-cyan-400">TTL: 64</span>
                </div>
                <div className="space-y-1 text-white/90">
                  <p><span className="text-[#38BDF8]">SRC_IP:</span> 192.168.1.104 <span className="text-white/40">(Client)</span></p>
                  <p><span className="text-[#38BDF8]">DST_IP:</span> 10.0.8.254 <span className="text-white/40">(Terminal B)</span></p>
                  <p><span className="text-[#38BDF8]">SEQ_NO:</span> 0x8F5D02A1 | <span className="text-[#10B981]">ALGO: BFS</span></p>
                </div>
                <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden relative">
                  <div className="absolute top-0 left-0 bg-[#2563EB] h-full w-[70%] animate-[pulse_2s_infinite]" />
                </div>
              </div>

              {/* Topology Summary */}
              <div className="flex items-start space-x-3 text-xs text-[#0F172A]/70 leading-relaxed">
                <Shield className="w-4.5 h-4.5 text-[#10B981] shrink-0 mt-0.5" />
                <span>
                  Our dynamic sandbox complies with IPv4 subnet simulation topologies. Use the controls below to inject, modify, and calculate paths.
                </span>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </section>
  );
}
