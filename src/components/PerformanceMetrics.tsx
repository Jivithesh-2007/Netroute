import React, { useState, useEffect } from 'react';
import { Activity, Server, Hash, FastForward, Clock, MailCheck, Milestone, HardDrive } from 'lucide-react';

export default function PerformanceMetrics() {
  const [nodesCount, setNodesCount] = useState(7);
  const [edgesCount, setEdgesCount] = useState(9);
  const [speed, setSpeed] = useState(1.42);
  const [execTime, setExecTime] = useState(0.024);
  const [delivered, setDelivered] = useState(1894);
  const [hopCount, setHopCount] = useState(3.2);
  const [memory, setMemory] = useState(48.2);

  // Subtly fluctuate the statistics to represent dynamic live network telemetry
  useEffect(() => {
    const timer = setInterval(() => {
      setSpeed(prev => parseFloat(Math.max(1.1, Math.min(1.8, prev + (Math.random() * 0.1 - 0.05))).toFixed(2)));
      setExecTime(prev => parseFloat(Math.max(0.015, Math.min(0.045, prev + (Math.random() * 0.004 - 0.002))).toFixed(4)));
      setDelivered(prev => prev + Math.floor(Math.random() * 3));
      setHopCount(prev => parseFloat(Math.max(2.8, Math.min(3.8, prev + (Math.random() * 0.2 - 0.1))).toFixed(1)));
      setMemory(prev => parseFloat(Math.max(45.0, Math.min(52.0, prev + (Math.random() * 0.4 - 0.2))).toFixed(1)));
    }, 2500);

    return () => clearInterval(timer);
  }, []);

  const metricsList = [
    { label: 'Active Routers (Nodes)', value: nodesCount, suffix: 'Devices', icon: Server, color: 'text-blue-600 bg-blue-50/40' },
    { label: 'Network Interconnects (Edges)', value: edgesCount, suffix: 'Fiber Links', icon: Hash, color: 'text-indigo-600 bg-indigo-50/40' },
    { label: 'Avg Traversal Speed', value: speed, suffix: 'm/s', icon: FastForward, color: 'text-sky-600 bg-sky-50/40' },
    { label: 'Routing Engine Latency', value: execTime, suffix: 'ms', icon: Clock, color: 'text-emerald-600 bg-emerald-50/40' },
    { label: 'Success Packets Delivered', value: delivered, suffix: 'pkts', icon: MailCheck, color: 'text-emerald-500 bg-emerald-50/20' },
    { label: 'Mean Hops Distance', value: hopCount, suffix: 'Hops', icon: Milestone, color: 'text-amber-600 bg-amber-50/40' },
    { label: 'Buffer Allocation', value: memory, suffix: 'KB', icon: HardDrive, color: 'text-rose-600 bg-rose-50/40' }
  ];

  return (
    <section className="py-24 bg-white border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#2563EB]/8 border border-[#2563EB]/15">
            <Activity className="w-4 h-4 text-[#2563EB]" />
            <span className="text-xs font-semibold text-[#2563EB] uppercase tracking-wider">
              Simulation Analytics
            </span>
          </div>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            Live Performance Metrics
          </h2>
          <p className="font-sans text-base text-[#0F172A]/70">
            Real-time simulated telemetry outputting performance data from the modular routing engine running inside your browser cache:
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {metricsList.map((metric, idx) => {
            const Icon = metric.icon;
            return (
              <div
                key={metric.label}
                className="bg-[#FAFBFC] border border-[#E5E7EB] rounded-2xl p-6.5 shadow-xs hover:border-[#2563EB]/25 hover:shadow-md transition-all duration-200 space-y-4"
                id={`metric-card-${idx}`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-[#0F172A]/50 uppercase tracking-wider block">
                    {metric.label}
                  </span>
                  <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${metric.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-2xl sm:text-3xl font-extrabold text-[#0F172A] tracking-tight font-headings block">
                    {metric.value}
                  </span>
                  <span className="font-mono text-[10px] text-gray-400 font-semibold uppercase tracking-wider block">
                    {metric.suffix}
                  </span>
                </div>
              </div>
            );
          })}

          {/* Quick interactive workload injection card */}
          <div className="bg-[#0F172A] text-white border border-white/10 rounded-2xl p-6 flex flex-col justify-between">
            <div className="space-y-2">
              <span className="text-[10px] text-[#38BDF8] font-bold uppercase tracking-wider font-mono">SIMULATION STRESS TEST</span>
              <p className="text-xs text-white/70 leading-relaxed">
                Manually push 100 extra routed packets through the pipeline to check peak router buffers and trace log integrity.
              </p>
            </div>
            <button
              onClick={() => {
                setDelivered(prev => prev + 100);
                setMemory(prev => parseFloat(Math.min(99.0, prev + 12.5).toFixed(1)));
              }}
              className="w-full bg-[#2563EB] hover:bg-white hover:text-[#0F172A] text-white py-2.5 rounded-xl text-xs font-bold transition-colors cursor-pointer"
            >
              Inject packet load
            </button>
          </div>

        </div>

      </div>
    </section>
  );
}
