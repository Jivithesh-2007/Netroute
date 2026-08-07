import React from 'react';
import { Network, Github, Linkedin, Mail, ShieldAlert } from 'lucide-react';

export default function Footer() {
  const handleScrollToTop = (e: React.MouseEvent) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="bg-[#0F172A] text-white border-t border-white/10 pt-16 pb-12 font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Footer Top Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 pb-12 border-b border-white/10 items-start">
          
          {/* Logo & description (5 cols) */}
          <div className="md:col-span-5 space-y-4">
            <a href="#" onClick={handleScrollToTop} className="flex items-center space-x-2.5">
              <div className="w-9 h-9 rounded-lg bg-[#2563EB] flex items-center justify-center text-white">
                <Network className="w-5 h-5" />
              </div>
              <span className="font-headings font-bold text-lg tracking-tight">
                NetRoute
              </span>
            </a>
            <p className="text-white/60 text-xs sm:text-sm leading-relaxed max-w-sm">
              An interactive learning laboratory designed to demonstrate vertices traversal protocols and graph routing cost algorithms (DFS & BFS) used for packet transmissions.
            </p>
          </div>

          {/* Project Spec Metadata (4 cols) */}
          <div className="md:col-span-4 space-y-2.5">
            <span className="block text-[10px] text-white/40 font-bold uppercase tracking-wider font-mono">Project Specification</span>
            <div className="space-y-1.5 text-xs text-white/80">
              <p><span className="text-white/40">Title:</span> Network Packet Routing</p>
              <p><span className="text-white/40">Industry:</span> Networking & Telecommunications</p>
              <p><span className="text-white/40">Developed For:</span> Micro Project Syllabus 06</p>
              <p><span className="text-white/40">Status:</span> Fully Compliant and Demonstrated</p>
            </div>
          </div>

          {/* Contact social icons (3 cols) */}
          <div className="md:col-span-3 space-y-3">
            <span className="block text-[10px] text-white/40 font-bold uppercase tracking-wider font-mono">Contact & Developer Links</span>
            <div className="flex items-center space-x-3.5 pt-1">
              <a
                href="https://github.com"
                target="_blank"
                rel="noreferrer"
                className="w-9 h-9 rounded-lg bg-white/5 hover:bg-[#2563EB] text-white flex items-center justify-center transition-colors"
                title="GitHub Repository"
              >
                <Github className="w-4.5 h-4.5" />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noreferrer"
                className="w-9 h-9 rounded-lg bg-white/5 hover:bg-[#2563EB] text-white flex items-center justify-center transition-colors"
                title="LinkedIn Profile"
              >
                <Linkedin className="w-4.5 h-4.5" />
              </a>
              <a
                href="mailto:developer@college.edu"
                className="w-9 h-9 rounded-lg bg-white/5 hover:bg-[#2563EB] text-white flex items-center justify-center transition-colors"
                title="Email Developer"
              >
                <Mail className="w-4.5 h-4.5" />
              </a>
            </div>
          </div>

        </div>

        {/* Footer Bottom Block (no copyright watermark) */}
        <div className="flex flex-col sm:flex-row items-center justify-between pt-8 gap-4 text-xs text-white/40 font-mono">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-amber-500/50" />
            <span>Academic Sandbox • Compiled with React + Vite + Tailwind</span>
          </div>
          <div className="flex items-center space-x-4">
            <a href="#" onClick={handleScrollToTop} className="hover:text-white transition-colors">
              Back to Top ↑
            </a>
          </div>
        </div>

      </div>
    </footer>
  );
}
