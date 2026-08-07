import React from 'react';
import {
  Globe, Network, Radio, Database, Cloud, Cpu, Wifi, ShieldAlert, Signal, Building2, Zap
} from 'lucide-react';

export default function RealWorldApplications() {
  const applications = [
    {
      title: 'Internet Routing',
      icon: Globe,
      desc: 'Enables global autonomous systems to interchange traffic. Algorithms form the basis of Border Gateway Protocol (BGP) routing tables.',
    },
    {
      title: 'ISP Core Networks',
      icon: Network,
      desc: 'Internet Service Providers leverage graph costs to shape customer traffic bandwidth, optimize throughput bounds, and perform load-balancing.',
    },
    {
      title: 'Telecommunications',
      icon: Radio,
      desc: 'Models signaling lanes and routing channels in voice-over-IP (VoIP) and cellular backhaul networks to maintain low jitter.',
    },
    {
      title: 'Enterprise Data Centers',
      icon: Database,
      desc: 'Manages East-West traffic pathways within virtualized server topologies, ensuring low-latency communication between web servers and storage nodes.',
    },
    {
      title: 'Cloud Computing Infrastructure',
      icon: Cloud,
      desc: 'Underpins Software-Defined Networks (SDN) in public clouds (AWS, GCP, Azure), allowing isolated tenant networks to map paths dynamically.',
    },
    {
      title: 'Internet of Things (IoT)',
      icon: Cpu,
      desc: 'Governs low-power, lossy mesh grids (RPL protocol) where tiny sensor nodes route telemetry back to local collection points with low overhead.',
    },
    {
      title: 'Wireless Networks',
      icon: Wifi,
      desc: 'Models radio frequency routing links and ad-hoc networks (MANET) where physical topology positions shift fluidly in space.',
    },
    {
      title: 'Military Communications',
      icon: ShieldAlert,
      desc: 'Enforces robust packet transmission protocols designed to self-heal and route around active terminal destruction during node failure.',
    },
    {
      title: 'Satellite Networks',
      icon: Signal,
      desc: 'Controls orbital satellite mesh networks (e.g. Starlink) where packet lasers shift rapidly based on Keplerian satellite position matrices.',
    },
    {
      title: 'Smart Cities',
      icon: Building2,
      desc: 'Optimizes telemetry pathways for traffic sensors, connected grids, waste management automation, and city fiber backbones.',
    }
  ];

  return (
    <section id="real-world" className="py-24 bg-[#FAFBFC] border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#2563EB]/8 border border-[#2563EB]/15">
            <Zap className="w-4 h-4 text-[#2563EB]" />
            <span className="text-xs font-semibold text-[#2563EB] uppercase tracking-wider">
              Industry Implementation
            </span>
          </div>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            Real-World Network Applications
          </h2>
          <p className="font-sans text-base text-[#0F172A]/70">
            Graph routing algorithms are not purely theoretical—they operate continuously in the background of almost every modern digital utility:
          </p>
        </div>

        {/* 10 Card Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {applications.map((app, idx) => {
            const AppIcon = app.icon;
            return (
              <div
                key={app.title}
                className="bg-white border border-[#E5E7EB] rounded-2xl p-6.5 hover:shadow-md hover:border-[#2563EB]/25 transition-all duration-200 flex flex-col justify-between"
                id={`app-card-${idx}`}
              >
                <div className="space-y-4">
                  {/* Icon */}
                  <div className="w-10 h-10 rounded-lg bg-[#FAFBFC] border border-[#E5E7EB] text-[#2563EB] flex items-center justify-center">
                    <AppIcon className="w-5 h-5" />
                  </div>

                  {/* Text */}
                  <div className="space-y-1.5">
                    <h3 className="font-headings text-sm font-bold text-[#0F172A]">
                      {app.title}
                    </h3>
                    <p className="font-sans text-xs text-[#0F172A]/70 leading-relaxed">
                      {app.desc}
                    </p>
                  </div>
                </div>

                <div className="pt-3 mt-4 border-t border-[#E5E7EB]/50 text-[10px] font-semibold text-[#2563EB] tracking-wider uppercase">
                  RFC Compliant
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
