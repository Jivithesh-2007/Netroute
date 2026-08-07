import React from 'react';
import { Database, GitFork, Minimize, ShieldCheck, HelpCircle } from 'lucide-react';

export default function TraditionalVsGraph() {
  return (
    <section className="py-24 bg-[#FAFBFC] border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider block">
            Architectural paradigms
          </span>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            Traditional Routing vs. Graph Routing
          </h2>
          <p className="font-sans text-base text-[#0F172A]/70">
            How does raw router silicon hardware compare to educational and dynamic software graph-routing simulators?
          </p>
        </div>

        {/* 2 Card Columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch">
          
          {/* Card 1: Traditional Routing */}
          <div className="bg-white border border-[#E5E7EB] rounded-2xl p-6 sm:p-8 space-y-6 shadow-xs hover:border-[#E5E7EB]/80 hover:shadow-md transition-all flex flex-col justify-between">
            <div className="space-y-4">
              {/* Icon & title */}
              <div className="flex items-center space-x-3 pb-4 border-b border-[#E5E7EB]">
                <div className="w-10 h-10 rounded-lg bg-[#0F172A]/5 flex items-center justify-center text-[#0F172A]">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-headings text-lg font-bold text-[#0F172A]">Traditional Router Hardware</h3>
                  <span className="font-sans text-xs text-[#0F172A]/50 font-semibold uppercase tracking-wider">Static & State-Bound</span>
                </div>
              </div>

              {/* Description */}
              <p className="font-sans text-sm text-[#0F172A]/70 leading-relaxed">
                Traditional routing is deployed directly on physical switch ASIC hardware and governed by standardized enterprise routing daemons. Paths are pre-calculated and cached locally within static SRAM banks.
              </p>

              {/* Bullet points */}
              <div className="space-y-3.5 pt-2">
                <div className="flex items-start space-x-3 text-xs">
                  <div className="w-5 h-5 rounded-md bg-[#0F172A]/5 text-[#0F172A] flex items-center justify-center font-bold shrink-0">1</div>
                  <p className="font-sans text-[#0F172A]/75 leading-relaxed">
                    <strong>Routing Tables:</strong> Uses static IP prefix matches (TCAM) which can lead to slow convergence under route flaps.
                  </p>
                </div>
                <div className="flex items-start space-x-3 text-xs">
                  <div className="w-5 h-5 rounded-md bg-[#0F172A]/5 text-[#0F172A] flex items-center justify-center font-bold shrink-0">2</div>
                  <p className="font-sans text-[#0F172A]/75 leading-relaxed">
                    <strong>Static Paths:</strong> Path overrides usually require manual administrative metric adjustments or static gateway binds.
                  </p>
                </div>
                <div className="flex items-start space-x-3 text-xs">
                  <div className="w-5 h-5 rounded-md bg-[#0F172A]/5 text-[#0F172A] flex items-center justify-center font-bold shrink-0">3</div>
                  <p className="font-sans text-[#0F172A]/75 leading-relaxed">
                    <strong>Protocol Dependent:</strong> Strictly restricted to pre-existing rigid protocols such as OSPF, BGP, or RIP.
                  </p>
                </div>
                <div className="flex items-start space-x-3 text-xs">
                  <div className="w-5 h-5 rounded-md bg-[#0F172A]/5 text-[#0F172A] flex items-center justify-center font-bold shrink-0">4</div>
                  <p className="font-sans text-[#0F172A]/75 leading-relaxed">
                    <strong>Limited Adaptability:</strong> Difficult to customize or re-engineer on the fly without reprogramming network equipment.
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-[#E5E7EB]">
              <span className="font-mono text-[10px] text-[#0F172A]/40 uppercase font-bold tracking-wider">Deploy: Enterprise WAN Core Switches</span>
            </div>
          </div>

          {/* Card 2: Graph Routing */}
          <div className="bg-white border border-[#2563EB]/25 rounded-2xl p-6 sm:p-8 space-y-6 shadow-md shadow-[#2563EB]/5 hover:shadow-lg transition-all flex flex-col justify-between">
            <div className="space-y-4">
              {/* Icon & title */}
              <div className="flex items-center space-x-3 pb-4 border-b border-[#2563EB]/15">
                <div className="w-10 h-10 rounded-lg bg-[#2563EB]/8 flex items-center justify-center text-[#2563EB]">
                  <GitFork className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-headings text-lg font-bold text-[#0F172A]">Algorithmic Graph Routing</h3>
                  <span className="font-sans text-xs text-[#2563EB] font-semibold uppercase tracking-wider">Dynamic & Visual</span>
                </div>
              </div>

              {/* Description */}
              <p className="font-sans text-sm text-[#0F172A]/70 leading-relaxed">
                Graph-based routing leverages math and algorithmic computation to discover and visualize optimal paths over arbitrary topologies, allowing software-defined networks (SDN) to adapt on demand.
              </p>

              {/* Bullet points */}
              <div className="space-y-3.5 pt-2">
                <div className="flex items-start space-x-3 text-xs">
                  <div className="w-5 h-5 rounded-md bg-[#2563EB]/10 text-[#2563EB] flex items-center justify-center font-bold shrink-0">1</div>
                  <p className="font-sans text-[#0F172A]/75 leading-relaxed">
                    <strong>Dynamic Adaptability:</strong> Recalculates cost matrices dynamically as edges are added, deleted, or re-weighted.
                  </p>
                </div>
                <div className="flex items-start space-x-3 text-xs">
                  <div className="w-5 h-5 rounded-md bg-[#2563EB]/10 text-[#2563EB] flex items-center justify-center font-bold shrink-0">2</div>
                  <p className="font-sans text-[#0F172A]/75 leading-relaxed">
                    <strong>Flexible Model Boundaries:</strong> Accommodates custom telemetry parameters (like latency, physical length, congestion, packet priority) instantly.
                  </p>
                </div>
                <div className="flex items-start space-x-3 text-xs">
                  <div className="w-5 h-5 rounded-md bg-[#2563EB]/10 text-[#2563EB] flex items-center justify-center font-bold shrink-0">3</div>
                  <p className="font-sans text-[#0F172A]/75 leading-relaxed">
                    <strong>Visual Verification:</strong> Allows operators to trace actual step-by-step queue pushes, stack pops, and backtracks visually.
                  </p>
                </div>
                <div className="flex items-start space-x-3 text-xs">
                  <div className="w-5 h-5 rounded-md bg-[#2563EB]/10 text-[#2563EB] flex items-center justify-center font-bold shrink-0">4</div>
                  <p className="font-sans text-[#0F172A]/75 leading-relaxed">
                    <strong>Educational Simulator Utility:</strong> Perfect for engineering education, sandbox simulation, and building custom routing software protocols.
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-[#E5E7EB]">
              <span className="font-mono text-[10px] text-[#2563EB] uppercase font-bold tracking-wider">Deploy: Software-Defined Networks (SDN)</span>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
