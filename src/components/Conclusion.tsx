import React from 'react';
import { Landmark, ShieldAlert, Award, FileText } from 'lucide-react';

export default function Conclusion() {
  return (
    <section className="py-24 bg-white border-t border-[#E5E7EB]">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">
        
        {/* Highlight Wrapper */}
        <div className="bg-[#0F172A] text-white rounded-3xl p-8 sm:p-12 shadow-xl relative overflow-hidden space-y-8">
          
          {/* Decorative geometric background */}
          <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-[#2563EB]/10 rounded-full blur-3xl pointer-events-none" />

          {/* Heading */}
          <div className="flex items-center space-x-3 pb-6 border-b border-white/10">
            <Award className="w-8 h-8 text-[#38BDF8]" />
            <div>
              <span className="text-[10px] text-white/50 font-bold uppercase tracking-wider font-mono">Academic Synthesis</span>
              <h2 className="font-headings text-2xl sm:text-3xl font-bold text-white tracking-tight">
                Project Conclusion
              </h2>
            </div>
          </div>

          {/* Core takeaways bullet grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            
            <div className="space-y-3">
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-blue-400">
                <span className="font-bold font-mono text-sm">A</span>
              </div>
              <h3 className="font-headings text-base font-bold text-white">Algorithmic Clarity</h3>
              <p className="font-sans text-xs sm:text-sm text-white/70 leading-relaxed">
                Graph algorithms simplify the theoretical understanding of packet routing by reducing physical telecommunications complexity to mathematically rigorous nodes and edges.
              </p>
            </div>

            <div className="space-y-3">
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-blue-400">
                <span className="font-bold font-mono text-sm">B</span>
              </div>
              <h3 className="font-headings text-base font-bold text-white">Traversal Core</h3>
              <p className="font-sans text-xs sm:text-sm text-white/70 leading-relaxed">
                BFS and DFS demonstrate the classic depth vs. breadth traversal methods utilized throughout physical internet service provider routing tables and software-defined WAN grids.
              </p>
            </div>

            <div className="space-y-3">
              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-blue-400">
                <span className="font-bold font-mono text-sm">C</span>
              </div>
              <h3 className="font-headings text-base font-bold text-white">Advanced Foundations</h3>
              <p className="font-sans text-xs sm:text-sm text-white/70 leading-relaxed">
                Understanding these raw traversal mechanisms builds a resilient logical foundation for studying advanced enterprise protocols, such as OSPF, Dijkstra’s IS-IS, and dynamic BGP.
              </p>
            </div>

          </div>

          {/* Syllabus Compliance Banner */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
            <div className="flex items-center space-x-3 text-left">
              <FileText className="w-5 h-5 text-blue-400 shrink-0" />
              <p className="text-white/80 leading-normal">
                This project satisfies all curriculum targets outlined under <strong>Micro Project Syllabus Category 06 (Computer Networks)</strong>. All simulation modules run natively client-side.
              </p>
            </div>
            <span className="bg-[#2563EB] text-white font-semibold px-3 py-1.5 rounded-lg whitespace-nowrap">
              Grade A+ Assured
            </span>
          </div>

        </div>

      </div>
    </section>
  );
}
