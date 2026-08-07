import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import AboutProject from './components/AboutProject';
import Objectives from './components/Objectives';
import GraphTheory from './components/GraphTheory';
import RoutingAlgorithms from './components/RoutingAlgorithms';
import Simulator from './components/Simulator';
import DfsBfsComparison from './components/DfsBfsComparison';
import TraditionalVsGraph from './components/TraditionalVsGraph';
import PacketFlowAnimation from './components/PacketFlowAnimation';
import RealWorldApplications from './components/RealWorldApplications';
import TechnologiesUsed from './components/TechnologiesUsed';
import LearningOutcomes from './components/LearningOutcomes';
import PerformanceMetrics from './components/PerformanceMetrics';
import Faq from './components/Faq';
import Conclusion from './components/Conclusion';
import Footer from './components/Footer';

export default function App() {
  const [activeSection, setActiveSection] = useState('hero');

  // Intersection Observer to highlight current section in Header
  useEffect(() => {
    const sections = [
      'about',
      'objectives',
      'graph-theory',
      'algorithms',
      'simulator',
      'dfs-vs-bfs',
      'packet-flow',
      'real-world'
    ];

    const observerOptions = {
      root: null,
      rootMargin: '-30% 0px -60% 0px', // trigger near center viewport
      threshold: 0
    };

    const handleIntersection = (entries: IntersectionObserverEntry[]) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setActiveSection(entry.target.id);
        }
      });
    };

    const observer = new IntersectionObserver(handleIntersection, observerOptions);

    sections.forEach(id => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => {
      sections.forEach(id => {
        const el = document.getElementById(id);
        if (el) observer.unobserve(el);
      });
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#FAFBFC] text-[#0F172A] font-sans antialiased selection:bg-[#2563EB]/10 selection:text-[#2563EB]">
      {/* Sticky Top Header */}
      <Header activeSection={activeSection} />

      {/* Main Page Blocks */}
      <main>
        {/* 1. Hero Landing Block */}
        <Hero />

        {/* 2. Core Concepts Info Cards */}
        <AboutProject />

        {/* 3. Targets and Scope */}
        <Objectives />

        {/* 4. Graph Theory Mathematical Primitives */}
        <GraphTheory />

        {/* 5. Traversal Routing Algorithms (DFS/BFS Deep Dive) */}
        <RoutingAlgorithms />

        {/* 6. Centerpiece Simulator Sandbox */}
        <Simulator />

        {/* 7. Comparison Table Grid */}
        <DfsBfsComparison />

        {/* 8. Hardware vs Graph Paradigm Contrast */}
        <TraditionalVsGraph />

        {/* 9. Interactive Hop Tracing Pipeline */}
        <PacketFlowAnimation />

        {/* 10. Real World Deployment Sectors */}
        <RealWorldApplications />

        {/* 11. Implemented Tech Stack Badges */}
        <TechnologiesUsed />

        {/* 12. Students Takeaway Learning Timeline */}
        <LearningOutcomes />

        {/* 13. Simulated Tickers Dashboard */}
        <PerformanceMetrics />

        {/* 14. Academic FAQs Accordion */}
        <Faq />

        {/* 15. Summary Academic Conclusion */}
        <Conclusion />
      </main>

      {/* 16. Footer (No watermark metadata block) */}
      <Footer />
    </div>
  );
}
