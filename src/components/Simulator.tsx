import React, { useState, useEffect, useRef } from 'react';
import {
  Play, RotateCcw, Shuffle, FileText, Trash2, PlusCircle, Link2, 
  ArrowRight, Shield, Cpu, Sparkles, Check, HelpCircle, Server, Zap
} from 'lucide-react';
import { Node, Edge, SimulationResult, TraversalStep } from '../types';
import { runDFS, runBFS, generateDefaultGraph, generateRandomGraph } from '../utils/routing';

export default function Simulator() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  
  // Editor States
  const [editorMode, setEditorMode] = useState<'navigate' | 'addNode' | 'delete'>('navigate');
  const [nodeNameInput, setNodeNameInput] = useState('');
  
  // Edge creator states
  const [edgeSource, setEdgeSource] = useState('');
  const [edgeTarget, setEdgeTarget] = useState('');
  const [edgeWeight, setEdgeWeight] = useState(5);
  
  // Routing settings
  const [sourceNode, setSourceNode] = useState('');
  const [destNode, setDestNode] = useState('');
  const [selectedAlgo, setSelectedAlgo] = useState<'DFS' | 'BFS'>('BFS');
  
  // Interactive selected node/edge
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  
  // Animation States
  const [isAnimating, setIsAnimating] = useState(false);
  const [animStepIndex, setAnimStepIndex] = useState(-1);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [animatedVisited, setAnimatedVisited] = useState<string[]>([]);
  const [animatedPath, setAnimatedPath] = useState<string[]>([]);
  const [animationSpeed, setAnimationSpeed] = useState(800); // ms per step
  
  // Packet animation along final path
  const [packetProgress, setPacketProgress] = useState(0);
  const [packetEdgeIndex, setPacketEdgeIndex] = useState(-1);
  const [showPacket, setShowPacket] = useState(false);

  const svgRef = useRef<SVGSVGElement>(null);

  // Initialize with standard sample graph
  useEffect(() => {
    const defaultGraph = generateDefaultGraph();
    setNodes(defaultGraph.nodes);
    setEdges(defaultGraph.edges);
    setSourceNode('N1');
    setDestNode('N7');
  }, []);

  // Sync edge builder defaults when nodes change
  useEffect(() => {
    if (nodes.length >= 2) {
      if (!edgeSource || !nodes.some(n => n.id === edgeSource)) setEdgeSource(nodes[0].id);
      if (!edgeTarget || !nodes.some(n => n.id === edgeTarget)) setEdgeTarget(nodes[1].id);
    }
  }, [nodes, edgeSource, edgeTarget]);

  // Handle Canvas click to add a node
  const handleCanvasClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (editorMode !== 'addNode' || !svgRef.current) return;
    
    const rect = svgRef.current.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);

    // Limit boundary to keep nodes within standard view box
    if (x < 30 || x > 770 || y < 30 || y > 370) return;

    // Generate unique ID and name
    const id = `N${Date.now().toString().slice(-4)}`;
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const customName = nodeNameInput.trim() || `Router ${letters[nodes.length % 26]}${nodes.length >= 26 ? Math.floor(nodes.length / 26) : ''}`;
    
    const newNode: Node = {
      id,
      name: customName,
      x,
      y
    };

    setNodes(prev => [...prev, newNode]);
    setNodeNameInput('');
    setEditorMode('navigate'); // Reset to navigate mode
  };

  // Node deletion or selection
  const handleNodeClick = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    if (editorMode === 'delete') {
      // Delete node and its corresponding edges
      setNodes(prev => prev.filter(n => n.id !== nodeId));
      setEdges(prev => prev.filter(edge => edge.source !== nodeId && edge.target !== nodeId));
      if (sourceNode === nodeId) setSourceNode('');
      if (destNode === nodeId) setDestNode('');
      if (selectedNodeId === nodeId) setSelectedNodeId(null);
    } else {
      setSelectedNodeId(nodeId);
      // Convenience auto-filler for link builder
      if (!edgeSource) {
        setEdgeSource(nodeId);
      } else if (edgeSource !== nodeId && !edgeTarget) {
        setEdgeTarget(nodeId);
      } else {
        setEdgeSource(nodeId);
        setEdgeTarget('');
      }
    }
  };

  // Edge deletion
  const handleDeleteEdge = (source: string, target: string) => {
    setEdges(prev => prev.filter(e => !(e.source === source && e.target === target) && !(e.source === target && e.target === source)));
  };

  // Add edge connection
  const handleAddEdge = (e: React.FormEvent) => {
    e.preventDefault();
    if (!edgeSource || !edgeTarget || edgeSource === edgeTarget) {
      alert("Please select two distinct routers.");
      return;
    }

    // Check if edge already exists
    const exists = edges.some(
      e => (e.source === edgeSource && e.target === edgeTarget) || (e.source === edgeTarget && e.target === edgeSource)
    );

    if (exists) {
      alert("A connection already exists between these two routers. Delete it first to re-assign weight.");
      return;
    }

    const newEdge: Edge = {
      source: edgeSource,
      target: edgeTarget,
      weight: Number(edgeWeight)
    };

    setEdges(prev => [...prev, newEdge]);
    setEdgeTarget(''); // Reset secondary selection helper
  };

  // Reset Graph
  const handleReset = () => {
    stopAnimation();
    const defaultGraph = generateDefaultGraph();
    setNodes(defaultGraph.nodes);
    setEdges(defaultGraph.edges);
    setSourceNode('N1');
    setDestNode('N7');
    setSelectedNodeId(null);
  };

  // Generate random graph
  const handleGenerateRandom = () => {
    stopAnimation();
    const rand = generateRandomGraph();
    setNodes(rand.nodes);
    setEdges(rand.edges);
    setSelectedNodeId(null);
    if (rand.nodes.length > 0) {
      setSourceNode(rand.nodes[0].id);
      setDestNode(rand.nodes[rand.nodes.length - 1].id);
    }
  };

  // Clear simulator overlays
  const handleClearSimulation = () => {
    stopAnimation();
  };

  const stopAnimation = () => {
    setIsAnimating(false);
    setAnimStepIndex(-1);
    setSimulationResult(null);
    setAnimatedVisited([]);
    setAnimatedPath([]);
    setShowPacket(false);
    setPacketProgress(0);
    setPacketEdgeIndex(-1);
  };

  // Trigger Routing Algorithm
  const handleFindPath = () => {
    if (!sourceNode || !destNode) {
      alert('Please specify both Source and Destination routers.');
      return;
    }
    if (sourceNode === destNode) {
      alert('Source and Destination are the same router.');
      return;
    }

    stopAnimation();

    // Run underlying logic
    const result = selectedAlgo === 'DFS' 
      ? runDFS(nodes, edges, sourceNode, destNode) 
      : runBFS(nodes, edges, sourceNode, destNode);

    setSimulationResult(result);
    setIsAnimating(true);
    setAnimStepIndex(0);
  };

  // Step-by-Step Traversal Tick
  useEffect(() => {
    if (!isAnimating || !simulationResult || animStepIndex < 0) return;

    const steps = simulationResult.steps;
    if (animStepIndex < steps.length) {
      const timer = setTimeout(() => {
        const currentStep = steps[animStepIndex];
        
        // Update visited nodes so far
        setAnimatedVisited(prev => {
          if (prev.includes(currentStep.nodeId)) return prev;
          return [...prev, currentStep.nodeId];
        });

        // Highlight current path traversal frontier
        setAnimatedPath(currentStep.pathSoFar);

        setAnimStepIndex(prev => prev + 1);
      }, animationSpeed);

      return () => clearTimeout(timer);
    } else {
      // Completed the search traversal steps
      setIsAnimating(false);
      
      // If path exists, start traveling packet animation!
      if (simulationResult.path.length > 0) {
        setShowPacket(true);
        setPacketEdgeIndex(0);
        setPacketProgress(0);
      }
    }
  }, [isAnimating, animStepIndex, simulationResult, animationSpeed]);

  // Traveling Packet Tick
  useEffect(() => {
    if (!showPacket || !simulationResult || packetEdgeIndex < 0) return;

    const path = simulationResult.path;
    if (packetEdgeIndex < path.length - 1) {
      const timer = setInterval(() => {
        setPacketProgress(prev => {
          if (prev >= 1) {
            setPacketEdgeIndex(idx => idx + 1);
            return 0;
          }
          return prev + 0.08; // speed of traveling packet dot
        });
      }, 50);

      return () => clearInterval(timer);
    } else {
      // Packet reached terminal destination
      const timer = setTimeout(() => {
        setPacketProgress(1);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [showPacket, packetEdgeIndex, simulationResult]);

  // Determine colors of elements inside editor
  const getNodeFill = (id: string) => {
    // Check if in final route path
    const isFinalPath = simulationResult && simulationResult.path.includes(id);
    // Check if currently animated search frontier
    const isCurrentFrontier = animatedPath[animatedPath.length - 1] === id;
    // Check if visited in animated search
    const isVisited = animatedVisited.includes(id);

    if (id === sourceNode) return '#2563EB'; // Blue source
    if (id === destNode) return '#10B981'; // Green destination
    if (isFinalPath) return '#2563EB'; // Final routing path
    if (isCurrentFrontier) return '#F59E0B'; // Amber current evaluating
    if (isVisited) return '#F59E0B'; // Amber visited
    return '#FFFFFF';
  };

  const getNodeStroke = (id: string) => {
    if (id === selectedNodeId) return '#0F172A'; // Black selection border
    if (id === sourceNode) return '#1E40AF';
    if (id === destNode) return '#065F46';
    if (simulationResult && simulationResult.path.includes(id)) return '#2563EB';
    if (animatedVisited.includes(id)) return '#D97706';
    return '#94A3B8';
  };

  const getEdgeStroke = (source: string, target: string) => {
    if (!simulationResult) return '#E5E7EB';

    const path = simulationResult.path;
    // Check if edge is in the highlighted shortest path
    let isPathEdge = false;
    for (let i = 0; i < path.length - 1; i++) {
      if (
        (path[i] === source && path[i + 1] === target) ||
        (path[i] === target && path[i + 1] === source)
      ) {
        isPathEdge = true;
        break;
      }
    }

    if (isPathEdge) return '#2563EB'; // Glow blue for final path
    
    // Check if edge was traversed in animated traversal
    let isTraversed = false;
    for (let i = 0; i < animatedVisited.length; i++) {
      const node = animatedVisited[i];
      const parent = simulationResult.steps.find(s => s.nodeId === node)?.parentId;
      if (parent && ((parent === source && node === target) || (parent === target && node === source))) {
        isTraversed = true;
        break;
      }
    }

    if (isTraversed) return '#F59E0B'; // Visited search branches
    return '#E5E7EB';
  };

  const getEdgeWidth = (source: string, target: string) => {
    if (!simulationResult) return 1.5;
    
    const path = simulationResult.path;
    for (let i = 0; i < path.length - 1; i++) {
      if (
        (path[i] === source && path[i + 1] === target) ||
        (path[i] === target && path[i + 1] === source)
      ) {
        return 3.5; // Thicker for final route
      }
    }
    return 1.5;
  };

  // Helper to draw packet dot on SVG
  const renderLivePacketNode = () => {
    if (!showPacket || !simulationResult || packetEdgeIndex < 0 || packetEdgeIndex >= simulationResult.path.length - 1) return null;
    
    const uId = simulationResult.path[packetEdgeIndex];
    const vId = simulationResult.path[packetEdgeIndex + 1];

    const nodeU = nodes.find(n => n.id === uId);
    const nodeV = nodes.find(n => n.id === vId);

    if (!nodeU || !nodeV) return null;

    // Linear interpolate coordinates
    const curX = nodeU.x + (nodeV.x - nodeU.x) * packetProgress;
    const curY = nodeU.y + (nodeV.y - nodeU.y) * packetProgress;

    return (
      <g>
        <circle cx={curX} cy={curY} r={8} fill="rgba(37, 99, 235, 0.3)" className="animate-ping" />
        <circle cx={curX} cy={curY} r={5} fill="#2563EB" stroke="#FFFFFF" strokeWidth="1.5" />
      </g>
    );
  };

  return (
    <section id="simulator" className="py-24 bg-[#FAFBFC] border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Title */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-6">
          <div className="max-w-xl text-left space-y-4">
            <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider block">
              Core Feature Sandbox
            </span>
            <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
              Interactive Routing Simulator
            </h2>
            <p className="font-sans text-sm sm:text-base text-[#0F172A]/70 leading-relaxed">
              Design custom network layouts by editing the graph workspace. Inject simulated node outages, rewire routes, adjust weight costs, select BFS/DFS, and watch packet sequences in action.
            </p>
          </div>
          <div className="flex flex-wrap gap-2.5 shrink-0">
            <button
              onClick={handleGenerateRandom}
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-white border border-[#E5E7EB] text-[#0F172A] hover:border-[#2563EB] transition-colors cursor-pointer"
            >
              <Shuffle className="w-3.5 h-3.5 text-[#2563EB]" />
              <span>Random Graph</span>
            </button>
            <button
              onClick={handleReset}
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-white border border-[#E5E7EB] text-[#0F172A] hover:border-red-500 hover:text-red-600 transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Graph</span>
            </button>
          </div>
        </div>

        {/* Dynamic Sandbox Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Interactive Workspace Panel (Left - 8 Cols) */}
          <div className="lg:col-span-8 space-y-4">
            
            {/* Toolbar Mode Switches */}
            <div className="bg-white border border-[#E5E7EB] rounded-2xl p-3.5 flex flex-wrap gap-2 items-center justify-between shadow-xs">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-[#0F172A]/50 uppercase tracking-wider px-2">
                  Mode:
                </span>
                <button
                  onClick={() => setEditorMode('navigate')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-colors ${
                    editorMode === 'navigate'
                      ? 'bg-[#0F172A] text-white'
                      : 'bg-[#FAFBFC] border border-[#E5E7EB] text-[#0F172A]/70 hover:bg-[#E5E7EB]/40'
                  }`}
                >
                  Select & Connect
                </button>
                <button
                  onClick={() => setEditorMode('addNode')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-colors flex items-center space-x-1 ${
                    editorMode === 'addNode'
                      ? 'bg-[#2563EB] text-white'
                      : 'bg-[#FAFBFC] border border-[#E5E7EB] text-[#0F172A]/70 hover:bg-[#E5E7EB]/40'
                  }`}
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  <span>Add Router</span>
                </button>
                <button
                  onClick={() => setEditorMode('delete')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-colors flex items-center space-x-1 ${
                    editorMode === 'delete'
                      ? 'bg-red-600 text-white shadow-xs'
                      : 'bg-[#FAFBFC] border border-[#E5E7EB] text-[#0F172A]/70 hover:bg-[#E5E7EB]/40'
                  }`}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Delete Mode</span>
                </button>
              </div>

              {/* Status Note */}
              <div className="text-right px-2 text-[11px] font-mono text-[#0F172A]/50 flex items-center space-x-1">
                <span className="w-2 h-2 rounded-full bg-[#2563EB]" />
                <span>
                  {editorMode === 'addNode' 
                    ? 'Click inside empty workspace space to place a Router' 
                    : editorMode === 'delete' 
                    ? 'Click any router to erase it' 
                    : 'Click a Router, then connect using controls'}
                </span>
              </div>
            </div>

            {/* SVG Canvas Workspace */}
            <div className="bg-white border border-[#E5E7EB] rounded-2xl shadow-xs overflow-hidden relative min-h-[380px] select-none">
              
              {/* Optional Empty state helper text */}
              {nodes.length === 0 && (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6 space-y-3 z-10 bg-white/90">
                  <Server className="w-10 h-10 text-gray-300" />
                  <p className="font-headings text-base font-bold text-[#0F172A]">Workspace Empty</p>
                  <p className="font-sans text-xs text-gray-500 max-w-xs">Click "Add Router" in toolbar above, then tap inside this workspace to spawn nodes.</p>
                </div>
              )}

              {/* SVG Stage */}
              <svg
                ref={svgRef}
                viewBox="0 0 800 400"
                className="w-full h-full min-h-[380px] cursor-crosshair relative z-0 bg-[#FAFBFC]/30"
                onClick={handleCanvasClick}
              >
                {/* 1. Draw Edges (Links) */}
                {edges.map((edge, index) => {
                  const sourceNodeObj = nodes.find(n => n.id === edge.source);
                  const targetNodeObj = nodes.find(n => n.id === edge.target);
                  if (!sourceNodeObj || !targetNodeObj) return null;

                  // Find mid-point to place weight badges
                  const midX = (sourceNodeObj.x + targetNodeObj.x) / 2;
                  const midY = (sourceNodeObj.y + targetNodeObj.y) / 2;

                  return (
                    <g key={`edge-${index}`}>
                      <line
                        x1={sourceNodeObj.x}
                        y1={sourceNodeObj.y}
                        x2={targetNodeObj.x}
                        y2={targetNodeObj.y}
                        stroke={getEdgeStroke(edge.source, edge.target)}
                        strokeWidth={getEdgeWidth(edge.source, edge.target)}
                        transition-all="true"
                        className="transition-all duration-300"
                      />
                      {/* Weight Badge */}
                      <rect
                        x={midX - 11}
                        y={midY - 9}
                        width="22"
                        height="18"
                        rx="4"
                        fill="#FFFFFF"
                        stroke="#E5E7EB"
                        strokeWidth="1"
                      />
                      <text
                        x={midX}
                        y={midY + 4}
                        fontSize="10"
                        fontFamily="monospace"
                        fontWeight="bold"
                        fill="#0F172A"
                        textAnchor="middle"
                      >
                        {edge.weight}
                      </text>
                    </g>
                  );
                })}

                {/* 2. Render Live Packet Traveling */}
                {renderLivePacketNode()}

                {/* 3. Draw Nodes (Routers) */}
                {nodes.map((node) => {
                  const isSource = node.id === sourceNode;
                  const isDest = node.id === destNode;
                  const isSelected = node.id === selectedNodeId;

                  return (
                    <g
                      key={node.id}
                      onClick={(e) => handleNodeClick(e, node.id)}
                      className="cursor-pointer group"
                    >
                      {/* Outer pulse halo for active simulation states */}
                      {(isSource || isDest) && (
                        <circle
                          cx={node.x}
                          cy={node.y}
                          r="22"
                          fill="none"
                          stroke={isSource ? '#2563EB' : '#10B981'}
                          strokeWidth="1.5"
                          strokeDasharray="4 2"
                          className="animate-[spin_10s_linear_infinite]"
                        />
                      )}

                      {/* Main Node bubble */}
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r="15"
                        fill={getNodeFill(node.id)}
                        stroke={getNodeStroke(node.id)}
                        strokeWidth={isSelected ? 2.5 : 1.5}
                        className="transition-all duration-300"
                      />

                      {/* Router Text label centered inside or below */}
                      <text
                        cx={node.x}
                        cy={node.y}
                        x={node.x}
                        y={node.y + 4}
                        fontSize="9"
                        fontWeight="bold"
                        fill={getNodeFill(node.id) === '#FFFFFF' ? '#0F172A' : '#FFFFFF'}
                        textAnchor="middle"
                        fontFamily="monospace"
                      >
                        {node.id}
                      </text>

                      {/* Elegant name label hovering above */}
                      <text
                        x={node.x}
                        y={node.y - 20}
                        fontSize="11"
                        fontWeight="600"
                        fill={isSource ? '#2563EB' : isDest ? '#10B981' : '#0F172A'}
                        textAnchor="middle"
                        fontFamily="Space Grotesk"
                      >
                        {node.name}
                        {isSource && ' (Src)'}
                        {isDest && ' (Dst)'}
                      </text>
                    </g>
                  );
                })}
              </svg>

              {/* Subtitle helper on SVG */}
              <div className="absolute bottom-3 left-4 text-[10px] bg-[#0F172A]/75 text-white/80 px-2.5 py-1 rounded-md font-mono flex items-center space-x-1.5 z-10">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping" />
                <span>Undirected LAN/WAN Graph topology layer</span>
              </div>
            </div>

            {/* Quick Link/Edge Creator (If nodes exist) */}
            {nodes.length >= 2 && (
              <form onSubmit={handleAddEdge} className="bg-white border border-[#E5E7EB] rounded-2xl p-5 shadow-xs grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-[#0F172A]/60 uppercase tracking-wider block">Connect From</label>
                  <select
                    value={edgeSource}
                    onChange={(e) => setEdgeSource(e.target.value)}
                    className="w-full bg-[#FAFBFC] border border-[#E5E7EB] rounded-xl px-3 py-2 text-xs font-semibold focus:border-[#2563EB]"
                  >
                    {nodes.map(n => (
                      <option key={n.id} value={n.id}>{n.id} - {n.name}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-[#0F172A]/60 uppercase tracking-wider block">Connect To</label>
                  <select
                    value={edgeTarget}
                    onChange={(e) => setEdgeTarget(e.target.value)}
                    className="w-full bg-[#FAFBFC] border border-[#E5E7EB] rounded-xl px-3 py-2 text-xs font-semibold focus:border-[#2563EB]"
                  >
                    {nodes.map(n => (
                      <option key={n.id} value={n.id}>{n.id} - {n.name}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-[#0F172A]/60 uppercase tracking-wider block">Link Cost/Weight</label>
                  <input
                    type="number"
                    min="1"
                    max="99"
                    value={edgeWeight}
                    onChange={(e) => setEdgeWeight(Number(e.target.value))}
                    className="w-full bg-[#FAFBFC] border border-[#E5E7EB] rounded-xl px-3 py-2 text-xs font-semibold focus:border-[#2563EB]"
                  />
                </div>

                <button
                  type="submit"
                  className="inline-flex items-center justify-center space-x-1.5 bg-[#0F172A] hover:bg-[#2563EB] text-white py-2 px-4 rounded-xl text-xs font-semibold cursor-pointer transition-colors"
                >
                  <Link2 className="w-3.5 h-3.5" />
                  <span>Build Link</span>
                </button>
              </form>
            )}

          </div>

          {/* Configuration & Statistics Panel (Right - 4 Cols) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* 1. Controller Config Box */}
            <div className="bg-white border border-[#E5E7EB] rounded-2xl p-5 shadow-xs space-y-5">
              <h3 className="font-headings text-base font-extrabold text-[#0F172A] flex items-center space-x-2">
                <Cpu className="w-4.5 h-4.5 text-[#2563EB]" />
                <span>Simulation Controller</span>
              </h3>

              <div className="space-y-4">
                {/* Source Selection */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-[#0F172A]/60 uppercase tracking-wider block">Source Node</label>
                    <select
                      value={sourceNode}
                      onChange={(e) => setSourceNode(e.target.value)}
                      className="w-full bg-[#FAFBFC] border border-[#E5E7EB] rounded-xl px-3 py-2 text-xs font-semibold focus:border-[#2563EB]"
                    >
                      <option value="">-- select --</option>
                      {nodes.map(n => (
                        <option key={n.id} value={n.id}>{n.id} ({n.name})</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-[#0F172A]/60 uppercase tracking-wider block">Dest Node</label>
                    <select
                      value={destNode}
                      onChange={(e) => setDestNode(e.target.value)}
                      className="w-full bg-[#FAFBFC] border border-[#E5E7EB] rounded-xl px-3 py-2 text-xs font-semibold focus:border-[#2563EB]"
                    >
                      <option value="">-- select --</option>
                      {nodes.map(n => (
                        <option key={n.id} value={n.id}>{n.id} ({n.name})</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Algorithm Selection */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-[#0F172A]/60 uppercase tracking-wider block">Routing Logic Algorithm</label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setSelectedAlgo('BFS')}
                      className={`py-2 rounded-xl text-xs font-bold border transition-colors cursor-pointer ${
                        selectedAlgo === 'BFS'
                          ? 'bg-[#2563EB]/8 border-[#2563EB] text-[#2563EB]'
                          : 'bg-white border-[#E5E7EB] text-[#0F172A]/70 hover:bg-[#FAFBFC]'
                      }`}
                    >
                      BFS (Breadth First)
                    </button>
                    <button
                      type="button"
                      onClick={() => setSelectedAlgo('DFS')}
                      className={`py-2 rounded-xl text-xs font-bold border transition-colors cursor-pointer ${
                        selectedAlgo === 'DFS'
                          ? 'bg-[#2563EB]/8 border-[#2563EB] text-[#2563EB]'
                          : 'bg-white border-[#E5E7EB] text-[#0F172A]/70 hover:bg-[#FAFBFC]'
                      }`}
                    >
                      DFS (Depth First)
                    </button>
                  </div>
                </div>

                {/* Animation Speed Selector */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-[10px] font-bold text-[#0F172A]/60 uppercase tracking-wider">
                    <span>Traversal Delay</span>
                    <span>{animationSpeed}ms</span>
                  </div>
                  <input
                    type="range"
                    min="100"
                    max="2000"
                    step="100"
                    value={animationSpeed}
                    onChange={(e) => setAnimationSpeed(Number(e.target.value))}
                    className="w-full accent-[#2563EB]"
                  />
                </div>

                {/* Actions Trigger */}
                <div className="flex space-x-2 pt-1.5">
                  <button
                    onClick={handleFindPath}
                    className="flex-1 inline-flex items-center justify-center space-x-2 bg-[#2563EB] hover:bg-[#0F172A] text-white py-3 rounded-xl text-sm font-bold shadow-md shadow-[#2563EB]/15 cursor-pointer transition-all"
                  >
                    <Play className="w-4 h-4 text-cyan-300" />
                    <span>Run Route Analysis</span>
                  </button>
                  
                  {simulationResult && (
                    <button
                      onClick={handleClearSimulation}
                      className="px-3 rounded-xl border border-[#E5E7EB] hover:bg-red-50 hover:border-red-300 hover:text-red-500 transition-all cursor-pointer"
                      title="Clear simulation state"
                    >
                      <Trash2 className="w-4.5 h-4.5" />
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* 2. Simulation Stats Output Box */}
            <div className="bg-white border border-[#E5E7EB] rounded-2xl p-5 shadow-xs space-y-4">
              <h3 className="font-headings text-base font-extrabold text-[#0F172A] flex items-center space-x-2">
                <FileText className="w-4.5 h-4.5 text-[#10B981]" />
                <span>Engine Telemetry Results</span>
              </h3>

              {simulationResult ? (
                <div className="space-y-4">
                  {/* Visual path display */}
                  <div className="p-3 bg-[#FAFBFC] border border-[#E5E7EB] rounded-xl space-y-1.5">
                    <span className="block text-[10px] font-bold text-[#0F172A]/50 uppercase tracking-wider">Calculated Path Route</span>
                    <div className="flex items-center flex-wrap gap-1.5">
                      {simulationResult.path.length > 0 ? (
                        simulationResult.path.map((node, idx) => (
                          <React.Fragment key={node}>
                            <span className="font-mono text-xs font-bold bg-[#0F172A] text-white px-2 py-0.5 rounded">
                              {node}
                            </span>
                            {idx < simulationResult.path.length - 1 && (
                              <ArrowRight className="w-3 h-3 text-[#2563EB]" />
                            )}
                          </React.Fragment>
                        ))
                      ) : (
                        <span className="text-xs text-red-500 font-semibold">Destination unreachable! No connection paths exist.</span>
                      )}
                    </div>
                  </div>

                  {/* Matrix metrics */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-[#FAFBFC] p-3 rounded-xl border border-[#E5E7EB]">
                      <span className="text-[10px] block text-gray-500 uppercase font-medium">Path Cost</span>
                      <span className="text-lg font-extrabold text-[#0F172A] font-headings">{simulationResult.totalCost}</span>
                    </div>
                    <div className="bg-[#FAFBFC] p-3 rounded-xl border border-[#E5E7EB]">
                      <span className="text-[10px] block text-gray-500 uppercase font-medium">Hops Count</span>
                      <span className="text-lg font-extrabold text-[#0F172A] font-headings">{simulationResult.totalHops}</span>
                    </div>
                    <div className="bg-[#FAFBFC] p-3 rounded-xl border border-[#E5E7EB]">
                      <span className="text-[10px] block text-gray-500 uppercase font-medium">Execution Latency</span>
                      <span className="text-xs font-bold text-emerald-600 font-mono">{simulationResult.executionTimeMs} ms</span>
                    </div>
                    <div className="bg-[#FAFBFC] p-3 rounded-xl border border-[#E5E7EB]">
                      <span className="text-[10px] block text-gray-500 uppercase font-medium">Total Visited Nodes</span>
                      <span className="text-lg font-extrabold text-[#0F172A] font-headings">{simulationResult.visitedNodes.length}</span>
                    </div>
                  </div>

                  {/* Traversal Order sequence */}
                  <div className="space-y-1">
                    <span className="block text-[10px] font-bold text-[#0F172A]/50 uppercase tracking-wider">Search Traversal Sequence</span>
                    <p className="font-mono text-[11px] bg-[#0F172A] text-white p-2.5 rounded-lg leading-relaxed max-h-[80px] overflow-y-auto">
                      {simulationResult.visitedOrder.join(' → ')}
                    </p>
                  </div>

                </div>
              ) : (
                <div className="text-center py-8 text-[#0F172A]/50 space-y-2">
                  <Sparkles className="w-8 h-8 text-[#2563EB]/25 mx-auto animate-pulse" />
                  <p className="text-xs font-bold">Simulator Dormant</p>
                  <p className="text-[11px] max-w-[200px] mx-auto">Select a source and destination, then click "Run Route Analysis" to start the visualization.</p>
                </div>
              )}
            </div>

            {/* Quick Editor Helpers */}
            <div className="bg-emerald-50/40 border border-emerald-100 rounded-2xl p-4.5 space-y-2.5 text-xs text-[#0F172A]/75">
              <span className="font-bold text-[#0F172A] uppercase tracking-wider text-[10px] block">Editor Help Tip:</span>
              <ul className="list-disc pl-4 space-y-1.5 leading-relaxed">
                <li>Choose <strong className="text-[#2563EB]">BFS</strong> to observe a ripple neighbor expansion.</li>
                <li>Choose <strong className="text-[#2563EB]">DFS</strong> to observe a single probe path diving deep first.</li>
                <li>Assign higher edge weights to simulate physical congestion over specific hops.</li>
              </ul>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
