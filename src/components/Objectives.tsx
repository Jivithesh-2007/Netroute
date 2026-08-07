import React from 'react';
import { Share2, Compass, GitCommit, Activity, Play, BookOpen } from 'lucide-react';

export default function Objectives() {
  const objectives = [
    {
      title: 'Implement Graph Routing',
      icon: Share2,
      desc: 'Build a modular, graph-theoretical backend representation in TypeScript where node sets and edge sets dynamically govern network state.',
      bg: 'bg-blue-50/40 text-blue-600'
    },
    {
      title: 'Find Optimal Paths',
      icon: Compass,
      desc: 'Formulate deterministic algorithms to calculate multi-hop pathways, proving how packets find their destination across arbitrary scales.',
      bg: 'bg-indigo-50/40 text-indigo-600'
    },
    {
      title: 'Compare DFS and BFS',
      icon: GitCommit,
      desc: 'Deeply evaluate the difference in traversal mechanics—depth-first search using stacks versus breadth-first search using queues.',
      bg: 'bg-cyan-50/40 text-cyan-600'
    },
    {
      title: 'Analyze Routing Efficiency',
      icon: Activity,
      desc: 'Measure execution speed (milliseconds), hop counts, queue memory footprints, and total path costs to identify networking bottlenecks.',
      bg: 'bg-emerald-50/40 text-emerald-600'
    },
    {
      title: 'Visualize Transmission',
      icon: Play,
      desc: 'Build high-fidelity fluid visual feedback where physical packets move node-to-node and visited vectors pulse with clear state changes.',
      bg: 'bg-sky-50/40 text-sky-600'
    },
    {
      title: 'Understand Networking Concepts',
      icon: BookOpen,
      desc: 'Demystify enterprise routing protocols (like OSPF, RIP, and BGP) by demonstrating how their underlying graph primitives operate in practice.',
      bg: 'bg-amber-50/40 text-amber-600'
    }
  ];

  return (
    <section id="objectives" className="py-24 bg-white border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header Title */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
          <div className="max-w-xl text-left space-y-4">
            <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider block">
              Core Targets
            </span>
            <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
              Project Objectives
            </h2>
            <p className="font-sans text-sm sm:text-base text-[#0F172A]/70 leading-relaxed">
              This academic micro-project is designed to bridge the gap between abstract computer science algorithms and physical network engineering paradigms.
            </p>
          </div>
          <div className="bg-[#FAFBFC] border border-[#E5E7EB] rounded-xl px-4 py-3 text-xs font-medium text-[#0F172A]/60 flex items-center space-x-2 shrink-0">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
            <span>Target Syllabus Scope: IEEE-802.3 Compliant</span>
          </div>
        </div>

        {/* Objectives 3-column Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {objectives.map((obj, idx) => {
            const Icon = obj.icon;
            return (
              <div
                key={obj.title}
                className="bg-[#FAFBFC] border border-[#E5E7EB] rounded-2xl p-6.5 hover:shadow-md hover:border-[#2563EB]/25 transition-all duration-200 space-y-5"
                id={`objective-card-${idx}`}
              >
                {/* Icon Badge */}
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${obj.bg} border border-current/10`}>
                  <Icon className="w-6 h-6" />
                </div>

                {/* Content */}
                <div className="space-y-2">
                  <h3 className="font-headings text-lg font-bold text-[#0F172A]">
                    {obj.title}
                  </h3>
                  <p className="font-sans text-sm text-[#0F172A]/70 leading-relaxed">
                    {obj.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
