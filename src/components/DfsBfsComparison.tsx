import React from 'react';
import { Columns, GitCompare, RefreshCcw } from 'lucide-react';

export default function DfsBfsComparison() {
  const tableData = [
    {
      metric: 'Traversal Pattern',
      dfs: 'Explores deeply down a single path branch before backtracking.',
      bfs: 'Explores level-by-level, covering all immediate neighbor routers first.'
    },
    {
      metric: 'Data Structure',
      dfs: 'Stack (LIFO - Last In First Out) or Recursion.',
      bfs: 'Queue (FIFO - First In First Out).'
    },
    {
      metric: 'Memory Complexity',
      dfs: 'O(d) - where d is the depth of the tree (More space-efficient for deep, narrow graphs).',
      bfs: 'O(bᵈ) - where b is branching factor (High memory usage to store adjacent frontiers).'
    },
    {
      metric: 'Shortest Path Guarantee',
      dfs: 'No. DFS does not guarantee finding the shortest path or optimal hop route.',
      bfs: 'Yes. BFS guarantees finding the minimum-hop shortest path on unweighted graphs.'
    },
    {
      metric: 'Routing Speed',
      dfs: 'Varies. Might find target instantly if it resides on the first deep path probed.',
      bfs: 'Optimal for nodes closer to the source; slower if target is located very deep.'
    },
    {
      metric: 'Scalability',
      dfs: 'Highly scalable for sparse, deep network graphs.',
      bfs: 'Poor scalability on massive, dense WAN graphs due to frontier buffer sizes.'
    },
    {
      metric: 'Queue / Stack Overflow Risk',
      dfs: 'Subject to Stack Overflow in deep recursion bounds.',
      bfs: 'Subject to Out-of-Memory crashes under high branching bounds.'
    },
    {
      metric: 'Primary Use Cases',
      dfs: 'Topological sorting, cycle detection, path validation, maze generation.',
      bfs: 'IP route path calculation, peer discovery, flooding broadcasts, GPS navigation.'
    },
    {
      metric: 'Edge Weight Compatibility',
      dfs: 'Does not support edge weights natively; needs modifications.',
      bfs: 'Does not support weights natively; requires Dijkstra upgrade for link costs.'
    }
  ];

  return (
    <section id="dfs-vs-bfs" className="py-24 bg-white border-t border-[#E5E7EB]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Title */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#2563EB]/8 border border-[#2563EB]/15">
            <GitCompare className="w-4 h-4 text-[#2563EB]" />
            <span className="text-xs font-semibold text-[#2563EB] uppercase tracking-wider">
              Comparative Analysis
            </span>
          </div>
          <h2 className="font-headings text-3xl sm:text-4xl font-extrabold text-[#0F172A] tracking-tight">
            DFS vs BFS Routing Metrics
          </h2>
          <p className="font-sans text-base text-[#0F172A]/70">
            A head-to-head architectural analysis comparing Depth-First Search and Breadth-First Search within standard routing protocols.
          </p>
        </div>

        {/* Table Container */}
        <div className="bg-[#FAFBFC] border border-[#E5E7EB] rounded-2xl overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse font-sans text-sm">
              
              {/* Header */}
              <thead>
                <tr className="bg-[#0F172A] text-white border-b border-[#E5E7EB]">
                  <th className="p-4 sm:p-5 font-headings font-bold text-xs uppercase tracking-wider w-1/4">Comparison Metric</th>
                  <th className="p-4 sm:p-5 font-headings font-bold text-xs uppercase tracking-wider text-blue-400 w-3/8 bg-blue-950/20">
                    Depth First Search (DFS)
                  </th>
                  <th className="p-4 sm:p-5 font-headings font-bold text-xs uppercase tracking-wider text-[#38BDF8] w-3/8">
                    Breadth First Search (BFS)
                  </th>
                </tr>
              </thead>

              {/* Body */}
              <tbody className="divide-y divide-[#E5E7EB] text-[#0F172A]">
                {tableData.map((row, index) => (
                  <tr key={index} className="hover:bg-white/50 transition-colors">
                    <td className="p-4 sm:p-5 font-bold text-xs text-[#0F172A]/80 bg-[#FAFBFC] uppercase tracking-wide border-r border-[#E5E7EB]/50">
                      {row.metric}
                    </td>
                    <td className="p-4 sm:p-5 leading-relaxed text-[#0F172A]/80 font-medium bg-blue-50/10 border-r border-[#E5E7EB]/50">
                      {row.dfs}
                    </td>
                    <td className="p-4 sm:p-5 leading-relaxed text-[#0F172A]/80 font-medium">
                      {row.bfs}
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        </div>

      </div>
    </section>
  );
}
