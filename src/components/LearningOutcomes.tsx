import React from 'react';
import { Landmark, GraduationCap, CheckCircle } from 'lucide-react';

export default function LearningOutcomes() {
  const outcomes = [
    {
      step: '01',
      title: 'Graph Traversal Primitives',
      desc: 'Master the fundamental logic of exploring network vertices systematically. Understand Stack and Queue mechanics in algorithmic memory structures.'
    },
    {
      step: '02',
      title: 'Core Telecommunication Networking',
      desc: 'Grasp the physical composition of subnets, routers, link costs, latency variables, IP addresses, and RFC communication constraints.'
    },
    {
      step: '03',
      title: 'Packet Routing & Headers',
      desc: 'Understand the lifecycle of a packet, including header structure, Hop constraints, and Time-to-Live (TTL) decrements across network boundaries.'
    },
    {
      step: '04',
      title: 'Deterministic Path Finding',
      desc: 'Formulate algorithmic approaches to resolve reachable route targets over dynamically shifting node graph grids.'
    },
    {
      step: '05',
      title: 'Mathematical Graph Implementation',
      desc: 'Model physical infrastructure in code using adjacency lists and cost matrices, analyzing time and space complexities.'
    },
    {
      step: '06',
      title: 'Comparative Algorithm Profiling',
      desc: 'Examine DFS versus BFS performance, mapping speed, memory footprints, and shortest-path guarantees.'
    },
    {
      step: '07',
      title: 'Interactive System Visualization',
      desc: 'Translate complex mathematical models into real-time fluid animations that display packet transmissions and visited vectors.'
    }
  ];

  return (
    <section className="py-24 bg-[#FAFBFC] border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#2563EB]/8 border border-[#2563EB]/15">
            <GraduationCap className="w-4 h-4 text-[#2563EB]" />
            <span className="text-xs font-semibold text-[#2563EB] uppercase tracking-wider">
              Educational Takeaways
            </span>
          </div>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            Learning Outcomes
          </h2>
          <p className="font-sans text-base text-[#0F172A]/70">
            By building and interacting with this micro-project, computer science students acquire key industry competencies:
          </p>
        </div>

        {/* Timeline Layout */}
        <div className="relative max-w-3xl mx-auto">
          {/* Center line */}
          <div className="absolute left-[20px] md:left-1/2 top-0 bottom-0 w-[2px] bg-gray-200 -translate-x-1/2 hidden md:block" />
          <div className="absolute left-[20px] top-0 bottom-0 w-[2px] bg-gray-200 block md:hidden" />

          {/* Timeline Nodes */}
          <div className="space-y-12">
            {outcomes.map((item, index) => {
              const isEven = index % 2 === 0;
              return (
                <div
                  key={item.step}
                  className={`flex flex-col md:flex-row items-stretch relative ${
                    isEven ? 'md:flex-row-reverse' : ''
                  }`}
                  id={`timeline-step-${item.step}`}
                >
                  
                  {/* Timeline Badge Dot */}
                  <div className="absolute left-[20px] md:left-1/2 w-10 h-10 rounded-full bg-white border-2 border-[#2563EB] text-[#2563EB] flex items-center justify-center font-mono text-xs font-bold -translate-x-1/2 z-10 shadow-xs">
                    {item.step}
                  </div>

                  {/* Empty space filler for desktop alignment */}
                  <div className="w-full md:w-1/2 hidden md:block" />

                  {/* Timeline content card */}
                  <div className="w-full md:w-1/2 pl-12 md:pl-0 md:px-8">
                    <div className="bg-white border border-[#E5E7EB] rounded-2xl p-6.5 shadow-xs hover:border-[#2563EB]/25 hover:shadow-md transition-all duration-200 text-left space-y-2.5">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4.5 h-4.5 text-[#10B981] shrink-0" />
                        <h3 className="font-headings text-base font-bold text-[#0F172A]">
                          {item.title}
                        </h3>
                      </div>
                      <p className="font-sans text-sm text-[#0F172A]/70 leading-relaxed">
                        {item.desc}
                      </p>
                    </div>
                  </div>

                </div>
              );
            })}
          </div>
        </div>

      </div>
    </section>
  );
}
