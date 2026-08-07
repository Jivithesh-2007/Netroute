import React, { useState, useEffect } from 'react';
import { Network, Menu, X, Cpu, Server, Activity } from 'lucide-react';

interface HeaderProps {
  activeSection: string;
}

export default function Header({ activeSection }: HeaderProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { label: 'About', href: '#about' },
    { label: 'Objectives', href: '#objectives' },
    { label: 'Graph Theory', href: '#graph-theory' },
    { label: 'Algorithms', href: '#algorithms' },
    { label: 'Simulator', href: '#simulator' },
    { label: 'DFS vs BFS', href: '#dfs-vs-bfs' },
    { label: 'Packet Flow', href: '#packet-flow' },
    { label: 'Real-World', href: '#real-world' }
  ];

  const handleScrollTo = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    const element = document.querySelector(id);
    if (element) {
      const offset = 80;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - offset;
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
    setIsOpen(false);
  };

  return (
    <header
      id="site-header"
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-[#FAFBFC]/90 backdrop-blur-md border-b border-[#E5E7EB] py-3 shadow-xs'
          : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <a
            href="#"
            onClick={(e) => handleScrollTo(e, '#hero')}
            className="flex items-center space-x-2.5 group"
            id="header-logo"
          >
            <div className="w-10 h-10 rounded-lg bg-[#2563EB] flex items-center justify-center text-white transition-transform group-hover:scale-105">
              <Network className="w-5.5 h-5.5" />
            </div>
            <div>
              <span className="font-headings font-extrabold text-xl tracking-tight text-[#0F172A] block leading-none">
                NetRoute <span className="text-[#2563EB]">Pro</span>
              </span>
              <span className="font-sans text-[10px] text-[#2563EB] font-bold tracking-widest block uppercase mt-1 leading-none">
                Micro Project 06
              </span>
            </div>
          </a>

          {/* Desktop Nav */}
          <nav className="hidden lg:flex items-center space-x-1" id="desktop-nav">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                onClick={(e) => handleScrollTo(e, item.href)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-250 ${
                  activeSection === item.href.replace('#', '')
                    ? 'text-[#2563EB] bg-[#2563EB]/5 font-semibold'
                    : 'text-[#0F172A]/70 hover:text-[#0F172A] hover:bg-[#E5E7EB]/40'
                }`}
              >
                {item.label}
              </a>
            ))}
          </nav>

          {/* Right Action Button */}
          <div className="hidden lg:flex items-center space-x-4">
            <a
              href="#simulator"
              onClick={(e) => handleScrollTo(e, '#simulator')}
              className="inline-flex items-center space-x-2 bg-[#0F172A] text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-[#2563EB] transition-colors duration-250 shadow-sm"
              id="header-cta"
            >
              <Cpu className="w-4 h-4 text-[#38BDF8]" />
              <span>Launch Simulator</span>
            </a>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex lg:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-lg text-[#0F172A]/70 hover:text-[#0F172A] hover:bg-[#E5E7EB]/50 focus:outline-none"
              id="mobile-menu-toggle"
              aria-label="Toggle menu"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav Drawer */}
      {isOpen && (
        <div className="lg:hidden absolute top-full left-0 right-0 bg-[#FAFBFC] border-b border-[#E5E7EB] shadow-lg animate-in fade-in slide-in-from-top-5 duration-200">
          <div className="px-4 pt-3 pb-6 space-y-1.5 sm:px-6">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                onClick={(e) => handleScrollTo(e, item.href)}
                className={`block px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                  activeSection === item.href.replace('#', '')
                    ? 'text-[#2563EB] bg-[#2563EB]/5 font-semibold'
                    : 'text-[#0F172A]/70 hover:text-[#0F172A] hover:bg-[#E5E7EB]/40'
                }`}
              >
                {item.label}
              </a>
            ))}
            <div className="pt-4 border-t border-[#E5E7EB] mt-4">
              <a
                href="#simulator"
                onClick={(e) => handleScrollTo(e, '#simulator')}
                className="flex items-center justify-center space-x-2 bg-[#2563EB] text-white py-3 px-4 rounded-lg text-base font-semibold hover:bg-[#0F172A] transition-colors shadow-sm"
                id="mobile-header-cta"
              >
                <Cpu className="w-5 h-5" />
                <span>Launch Simulator</span>
              </a>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
