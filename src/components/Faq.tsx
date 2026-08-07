import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';

export default function Faq() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs = [
    {
      q: 'What is packet routing?',
      a: 'Packet routing is the process of selecting paths in a network along which to send data packets. It is the fundamental mechanism that allows data to find its way from a sender (like your browser) to a destination server (like a website database) over several physical devices called routers.'
    },
    {
      q: 'Why use Breadth-First Search (BFS) in routing?',
      a: 'BFS is highly useful in unweighted network routing because it explores level-by-level, ensuring that it finds the path with the absolute minimum number of device hops. This translates directly to minimized network hops, which reduces processing delays at intermediate interfaces.'
    },
    {
      q: 'Why use Depth-First Search (DFS) in routing?',
      a: 'DFS is rarely used for primary packet forwarding because it does not guarantee shortest-hop paths. However, routers rely heavily on DFS internally for vital supplementary tasks, such as detecting illegal loops, identifying topological dependencies, and auditing overall graph connectivity.'
    },
    {
      q: 'Between DFS and BFS, which algorithm is faster?',
      a: 'The speed depends on the location of the destination node. BFS is faster if the target router is located physically closer to the source. DFS is faster if the target is located very deep along the first search path branch. In terms of memory usage, DFS uses significantly less memory than BFS on dense networks.'
    },
    {
      q: 'How are physical routers represented in a graph model?',
      a: 'Routers are represented mathematically as Vertices (V) or Nodes. The physical transmission lines (Ethernet, copper, coaxial, fiber-optic) connecting them are represented as Edges (E). The properties of these lines, like bandwidth limit or distance cost, are represented as Edge Weights.'
    },
    {
      q: 'Can graph routing replace traditional hardware routing tables?',
      a: 'No, they work together. Hardware routing tables (like Forwarding Information Bases or FIBs) are the high-speed physical lookup tables used by chips to forward packets at wire speed. Graph-based routing algorithms (part of the Control Plane) are used to compute those static tables dynamically whenever network conditions shift.'
    }
  ];

  return (
    <section id="faq" className="py-24 bg-[#FAFBFC] border-t border-[#E5E7EB]">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        
        {/* Title */}
        <div className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#2563EB]/8 border border-[#2563EB]/15">
            <HelpCircle className="w-4 h-4 text-[#2563EB]" />
            <span className="text-xs font-semibold text-[#2563EB] uppercase tracking-wider">
              Common Inquiries
            </span>
          </div>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            Frequently Asked Questions
          </h2>
          <p className="font-sans text-sm sm:text-base text-[#0F172A]/70 max-w-2xl mx-auto">
            Deepen your understanding of graph theory, routing algorithms, and core networking fundamentals with these detailed answers:
          </p>
        </div>

        {/* Accordion List */}
        <div className="space-y-4">
          {faqs.map((faq, idx) => {
            const isOpen = openIndex === idx;
            return (
              <div
                key={idx}
                className="bg-white border border-[#E5E7EB] rounded-2xl overflow-hidden shadow-xs transition-all duration-200"
                id={`faq-item-${idx}`}
              >
                <button
                  onClick={() => setOpenIndex(isOpen ? null : idx)}
                  className="w-full text-left px-6 py-5 flex items-center justify-between hover:bg-[#FAFBFC] transition-colors cursor-pointer"
                >
                  <span className="font-headings text-base font-bold text-[#0F172A]">
                    {faq.q}
                  </span>
                  <div className="text-[#2563EB]">
                    {isOpen ? <ChevronUp className="w-4.5 h-4.5" /> : <ChevronDown className="w-4.5 h-4.5" />}
                  </div>
                </button>

                {isOpen && (
                  <div className="px-6 pb-6 pt-1 text-sm text-[#0F172A]/75 leading-relaxed font-sans border-t border-[#E5E7EB]/50 animate-in fade-in duration-200">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
