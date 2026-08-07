import React, { useState, useEffect } from 'react';
import { Laptop, Server, Cpu, CheckCircle, Play, RotateCcw, ArrowRight, Layers, FileText } from 'lucide-react';

export default function PacketFlowAnimation() {
  const [currentHop, setCurrentHop] = useState<number>(-1); // -1 = idle, 0 = computer, 1 = R1, 2 = R2, 3 = R3, 4 = Destination
  const [ttl, setTtl] = useState<number>(64);
  const [log, setLog] = useState<string[]>(['Click "Initiate Flow" to trigger packet transmission.']);
  const [showHeader, setShowHeader] = useState<boolean>(true);

  const steps = [
    { name: 'Computer A', icon: Laptop, ip: '192.168.1.10' },
    { name: 'Router 1', icon: Cpu, ip: '10.0.1.1' },
    { name: 'Router 2', icon: Cpu, ip: '10.0.2.1' },
    { name: 'Router 3', icon: Cpu, ip: '10.0.3.1' },
    { name: 'Destination', icon: Server, ip: '8.8.8.8' }
  ];

  // Logic to simulate the step advances
  const handleNextHop = () => {
    if (currentHop >= 4) {
      // Completed, do nothing or reset
      return;
    }

    const next = currentHop + 1;
    setCurrentHop(next);

    if (next === 0) {
      setTtl(64);
      setLog([
        'Packet initialized at Computer A.',
        'Header: Source IP 192.168.1.10 | Dest IP 8.8.8.8.',
        'Initial TTL (Time to Live) set to 64.'
      ]);
    } else if (next === 1) {
      setTtl(63);
      setLog(prev => [
        ...prev,
        'Arrived at Gateway Router 1. Inspecting destination subnet...',
        'Inbound route match. TTL decremented from 64 to 63.'
      ]);
    } else if (next === 2) {
      setTtl(62);
      setLog(prev => [
        ...prev,
        'Hipped to core Router 2 via Fiber Interface.',
        'Routing table evaluated. TTL decremented from 63 to 62.'
      ]);
    } else if (next === 3) {
      setTtl(61);
      setLog(prev => [
        ...prev,
        'Traversing edge Router 3. Prepping final ethernet delivery.',
        'Next-hop matches destination server. TTL decremented from 62 to 61.'
      ]);
    } else if (next === 4) {
      setLog(prev => [
        ...prev,
        'Packet successfully delivered to Target Server (8.8.8.8)!',
        'TCP Handshake handshake accepted. Port 443 Session Established.'
      ]);
    }
  };

  const handleResetFlow = () => {
    setCurrentHop(-1);
    setTtl(64);
    setLog(['Click "Initiate Flow" to trigger packet transmission.']);
  };

  // Auto trigger interval for a hands-free flow
  const handleAutoRun = () => {
    handleResetFlow();
    let hop = -1;
    const interval = setInterval(() => {
      hop++;
      if (hop <= 4) {
        setCurrentHop(hop);
        // Sync logs and TTL
        if (hop === 0) {
          setTtl(64);
          setLog([
            'Packet initialized at Computer A.',
            'Header: Source IP 192.168.1.10 | Dest IP 8.8.8.8.',
            'Initial TTL (Time to Live) set to 64.'
          ]);
        } else if (hop === 1) {
          setTtl(63);
          setLog(prev => [...prev, 'Arrived at Gateway Router 1. Subnet verified. TTL decremented to 63.']);
        } else if (hop === 2) {
          setTtl(62);
          setLog(prev => [...prev, 'Traversed to Router 2. Routing table evaluated. TTL decremented to 62.']);
        } else if (hop === 3) {
          setTtl(61);
          setLog(prev => [...prev, 'Arrived at edge Router 3. Prepped local delivery. TTL decremented to 61.']);
        } else if (hop === 4) {
          setLog(prev => [...prev, 'Packet successfully delivered to Target Server (8.8.8.8)!']);
        }
      } else {
        clearInterval(interval);
      }
    }, 1500);
  };

  return (
    <section id="packet-flow" className="py-24 bg-white border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider block">
            Visual Pipeline Trace
          </span>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            Network Packet Flow Trace
          </h2>
          <p className="font-sans text-base text-[#0F172A]/70">
            Follow the physical routing pipeline. Observe how router registers modify the packet header, decrease TTL parameters, and establish connections:
          </p>
        </div>

        {/* Animation Display Card */}
        <div className="bg-[#FAFBFC] border border-[#E5E7EB] rounded-2xl p-6 sm:p-10 shadow-xs space-y-12">
          
          {/* 1. Step Pipeline Visual */}
          <div className="relative flex flex-col md:flex-row items-center justify-between gap-8 md:gap-4 md:px-6">
            
            {/* Background Line */}
            <div className="absolute top-[28px] left-[30px] right-[30px] h-[3px] bg-gray-200 hidden md:block z-0" />

            {/* Dynamic Sliding Packet Path Highlighter */}
            {currentHop >= 0 && (
              <div
                className="absolute top-[28px] left-[30px] h-[3px] bg-[#2563EB] hidden md:block z-0 transition-all duration-500"
                style={{ width: `${(currentHop / 4) * 85}%` }}
              />
            )}

            {/* Nodes Map */}
            {steps.map((step, idx) => {
              const StepIcon = step.icon;
              const isActive = idx === currentHop;
              const isPassed = idx < currentHop;
              const isUpcoming = idx > currentHop;

              return (
                <div key={step.name} className="flex flex-col items-center text-center relative z-10 w-[140px]">
                  
                  {/* Node Badge Bubble */}
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center transition-all duration-300 ${
                    isActive 
                      ? 'bg-[#2563EB] text-white border-4 border-blue-100 ring-2 ring-[#2563EB]'
                      : isPassed 
                      ? 'bg-[#0F172A] text-white border-2 border-white shadow-xs'
                      : 'bg-white text-gray-400 border-2 border-gray-200'
                  }`}>
                    <StepIcon className="w-6 h-6" />
                  </div>

                  {/* Title and IP info */}
                  <div className="mt-3.5 space-y-0.5">
                    <span className={`block font-headings text-sm font-bold ${isActive ? 'text-[#2563EB]' : 'text-[#0F172A]'}`}>
                      {step.name}
                    </span>
                    <span className="block font-mono text-[10px] text-[#0F172A]/50">
                      {step.ip}
                    </span>
                  </div>

                  {/* Little indicator under the active element */}
                  {isActive && (
                    <span className="absolute -bottom-6 text-[10px] bg-[#2563EB]/8 text-[#2563EB] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider animate-bounce">
                      Active Hop
                    </span>
                  )}
                </div>
              );
            })}

          </div>

          {/* 2. Interactive Console & Packet Header details */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch pt-6 border-t border-[#E5E7EB]">
            
            {/* Header Details Panel (Left) */}
            <div className="lg:col-span-5 bg-[#0F172A] text-white p-5 rounded-2xl space-y-4 font-mono text-xs flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-white/10 pb-2 mb-3">
                  <span className="text-white/40 text-[10px] font-bold">MUTATED HEADER REGISTERS</span>
                  <span className="text-cyan-400 font-bold">IPv4 DATAGRAM</span>
                </div>
                
                {currentHop >= 0 ? (
                  <div className="space-y-2 text-white/90">
                    <p><span className="text-white/40">PROTOCOL:</span> TCP (0x06)</p>
                    <p><span className="text-white/40">SOURCE IP:</span> 192.168.1.10</p>
                    <p><span className="text-white/40">DEST IP  :</span> 8.8.8.8</p>
                    <p className="flex items-center space-x-1.5">
                      <span className="text-white/40">TIME TO LIVE (TTL):</span> 
                      <span className="text-amber-400 font-bold bg-white/10 px-1.5 py-0.5 rounded">{ttl}</span>
                      {currentHop > 0 && <span className="text-xs text-[#10B981] font-bold">(-{currentHop})</span>}
                    </p>
                    <p><span className="text-white/40">STATUS   :</span> {currentHop === 4 ? 'SUCCESSFULLY DELIVERED' : 'TRANSITING'}</p>
                  </div>
                ) : (
                  <div className="text-center py-6 text-white/30 space-y-2">
                    <FileText className="w-6 h-6 mx-auto opacity-30" />
                    <span>No active transmission. Click start to populate registers.</span>
                  </div>
                )}
              </div>

              {/* Progress Bar indicator */}
              <div className="space-y-1 pt-4 border-t border-white/10">
                <div className="flex justify-between text-[10px] text-white/50">
                  <span>TRANSMISSION PROGRESS</span>
                  <span>{currentHop >= 0 ? (currentHop / 4) * 100 : 0}%</span>
                </div>
                <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden relative">
                  <div 
                    className="absolute top-0 left-0 bg-[#2563EB] h-full transition-all duration-300"
                    style={{ width: `${currentHop >= 0 ? (currentHop / 4) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Trace logs Console (Right) */}
            <div className="lg:col-span-7 bg-white border border-[#E5E7EB] p-5 rounded-2xl flex flex-col justify-between">
              
              <div className="space-y-2">
                <span className="text-xs font-bold text-[#0F172A]/50 uppercase tracking-wider block">Terminal Trace Outputs</span>
                <div className="font-mono text-xs text-[#0F172A]/85 bg-[#FAFBFC] border border-[#E5E7EB] p-3 rounded-xl max-h-[160px] overflow-y-auto space-y-1.5">
                  {log.map((line, index) => (
                    <p key={index} className="flex items-start space-x-1.5">
                      <span className="text-blue-500 font-bold font-mono select-none">&gt;</span>
                      <span>{line}</span>
                    </p>
                  ))}
                </div>
              </div>

              {/* Controller buttons */}
              <div className="flex space-x-2 pt-4 border-t border-[#E5E7EB]/50 mt-4">
                <button
                  onClick={handleAutoRun}
                  className="inline-flex items-center justify-center space-x-1.5 bg-[#2563EB] hover:bg-[#0F172A] text-white px-4 py-2.5 rounded-xl text-xs font-semibold cursor-pointer transition-colors"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Initiate Flow (Auto Loop)</span>
                </button>
                <button
                  onClick={handleNextHop}
                  disabled={currentHop >= 4}
                  className="inline-flex items-center justify-center space-x-1 px-4 py-2.5 rounded-xl text-xs font-semibold bg-[#FAFBFC] border border-[#E5E7EB] text-[#0F172A] hover:border-[#2563EB] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transition-colors"
                >
                  <span>Manual Step Hop</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={handleResetFlow}
                  className="p-2.5 rounded-xl border border-[#E5E7EB] text-[#0F172A]/70 hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition-colors cursor-pointer"
                  title="Reset pipeline"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </div>

            </div>

          </div>

          {/* Successful delivery banner */}
          {currentHop === 4 && (
            <div className="bg-[#10B981]/8 border border-[#10B981]/20 rounded-xl p-4 flex items-center space-x-3.5 text-xs text-[#0F172A]/80 animate-in fade-in duration-300">
              <CheckCircle className="w-5.5 h-5.5 text-[#10B981] shrink-0" />
              <span>
                <strong>Success!</strong> The routing trace packet reached the server without packet drop loops. Network path convergence verified successfully.
              </span>
            </div>
          )}

        </div>

      </div>
    </section>
  );
}
