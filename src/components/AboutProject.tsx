import React from 'react';
import { Package, Server, CircleDot, Link, Milestone, Scale, Timer, Binary, Network } from 'lucide-react';

export default function AboutProject() {
  const concepts = [
    {
      title: 'Packet',
      icon: Package,
      desc: 'The fundamental unit of data transmitted over a network. Each packet contains header metadata (source, destination IP, sequence number, TTL) and the actual message payload.',
      example: 'E.g., A 1500-byte IP Datagram'
    },
    {
      title: 'Router',
      icon: Server,
      desc: 'A specialized networking device that forwards data packets between computer networks. Routers inspect headers and use algorithms to choose the best path.',
      example: 'E.g., Cisco ISR 4000 edge router'
    },
    {
      title: 'Node',
      icon: CircleDot,
      desc: 'An active connection point or endpoint within a network graph. In our simulator, nodes represent host servers, local client switches, or intermediate routers.',
      example: 'E.g., Host server at 10.0.0.1'
    },
    {
      title: 'Edge',
      icon: Link,
      desc: 'The physical or wireless communication link connecting two routers/nodes. Edges are parameterized by physical characteristics like medium and length.',
      example: 'E.g., Fiber optic link or Ethernet'
    },
    {
      title: 'Hop',
      icon: Milestone,
      desc: 'The trip a packet takes from one router or intermediate network device to the next on its path from source to destination. Hops count physical transitions.',
      example: 'E.g., Source → R1 → R2 (2 Hops)'
    },
    {
      title: 'Cost',
      icon: Scale,
      desc: 'A quantitative weight assigned to an edge. Cost can represent financial price, distance, or a combined metric reflecting bandwidth and preference.',
      example: 'E.g., Dynamic OSPF cost matrix value'
    },
    {
      title: 'Latency',
      icon: Timer,
      desc: 'The time delay incurred for a packet to travel across a link. Latency depends on propagation delay, queuing, serialization, and router processing time.',
      example: 'E.g., 12ms ping time over WAN'
    },
    {
      title: 'Routing Table',
      icon: Binary,
      desc: 'A local database stored inside a router that maps destination IP subnets to specific outbound network interfaces or next-hop IP addresses.',
      example: 'E.g., Static route: 0.0.0.0/0 via R1'
    }
  ];

  return (
    <section id="about" className="py-24 bg-[#FAFBFC] border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#2563EB]/8 border border-[#2563EB]/15">
            <Network className="w-4 h-4 text-[#2563EB]" />
            <span className="text-xs font-semibold text-[#2563EB] uppercase tracking-wider">
              Core Networking Fundamentals
            </span>
          </div>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            What is Network Packet Routing?
          </h2>
          <p className="font-sans text-base sm:text-lg text-[#0F172A]/70 leading-relaxed">
            Routing is the backbone of the global internet. It is the process of forwarding information packets across multiple hops until they reach their destination. Below are the foundational building blocks of telecommunication graphs:
          </p>
        </div>

        {/* 8 Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {concepts.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={item.title}
                className="group relative bg-white border border-[#E5E7EB] rounded-2xl p-6 shadow-xs hover:shadow-md hover:border-[#2563EB]/30 transition-all duration-200 flex flex-col justify-between"
                id={`about-card-${idx}`}
              >
                <div>
                  {/* Icon Circle */}
                  <div className="w-11 h-11 rounded-xl bg-[#FAFBFC] border border-[#E5E7EB] group-hover:bg-[#2563EB]/10 group-hover:border-[#2563EB]/20 flex items-center justify-center text-[#0F172A] group-hover:text-[#2563EB] transition-colors duration-200 mb-5">
                    <Icon className="w-5.5 h-5.5" />
                  </div>

                  {/* Title & Desc */}
                  <h3 className="font-headings text-lg font-bold text-[#0F172A] mb-2 group-hover:text-[#2563EB] transition-colors">
                    {item.title}
                  </h3>
                  <p className="font-sans text-sm text-[#0F172A]/75 leading-relaxed mb-4">
                    {item.desc}
                  </p>
                </div>

                {/* Sub-label/Example - IBM style */}
                <div className="pt-3 border-t border-[#E5E7EB]/50">
                  <span className="font-mono text-[11px] text-[#0F172A]/50 font-medium tracking-wide">
                    {item.example}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
