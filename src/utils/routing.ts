import { Node, Edge, SimulationResult, TraversalStep } from '../types';

// Helper to build adjacency list representation
export function buildAdjacencyList(nodes: Node[], edges: Edge[]): Record<string, { target: string; weight: number }[]> {
  const adj: Record<string, { target: string; weight: number }[]> = {};
  
  nodes.forEach(n => {
    adj[n.id] = [];
  });

  edges.forEach(e => {
    if (adj[e.source]) {
      adj[e.source].push({ target: e.target, weight: e.weight });
    }
    // Undirected graph behavior for simulator: edges are bidirectional
    if (adj[e.target]) {
      adj[e.target].push({ target: e.source, weight: e.weight });
    }
  });

  // Sort neighbors by name or ID to make traversals deterministic and clean
  Object.keys(adj).forEach(key => {
    adj[key].sort((a, b) => {
      const nodeA = nodes.find(n => n.id === a.target)?.name || '';
      const nodeB = nodes.find(n => n.id === b.target)?.name || '';
      return nodeA.localeCompare(nodeB);
    });
  });

  return adj;
}

// DFS implementation with telemetry recording
export function runDFS(
  nodes: Node[],
  edges: Edge[],
  sourceId: string,
  destinationId: string
): SimulationResult {
  const startTime = performance.now();
  const adj = buildAdjacencyList(nodes, edges);
  
  const visitedOrder: string[] = [];
  const steps: TraversalStep[] = [];
  const visitedSet = new Set<string>();
  
  let finalPath: string[] = [];
  let found = false;

  function dfsHelper(currentId: string, path: string[], parentId: string | null) {
    if (found) return;

    visitedSet.add(currentId);
    visitedOrder.push(currentId);
    
    steps.push({
      nodeId: currentId,
      action: currentId === destinationId ? 'found' : 'visit',
      parentId,
      pathSoFar: [...path, currentId]
    });

    if (currentId === destinationId) {
      found = true;
      finalPath = [...path, currentId];
      return;
    }

    const neighbors = adj[currentId] || [];
    for (const neighbor of neighbors) {
      if (!visitedSet.has(neighbor.target) && !found) {
        dfsHelper(neighbor.target, [...path, currentId], currentId);
      }
    }

    if (!found) {
      steps.push({
        nodeId: currentId,
        action: 'backtrack',
        parentId,
        pathSoFar: [...path]
      });
    }
  }

  if (nodes.some(n => n.id === sourceId)) {
    dfsHelper(sourceId, [], null);
  }

  const endTime = performance.now();

  // Calculate path cost
  let totalCost = 0;
  if (finalPath.length > 0) {
    for (let i = 0; i < finalPath.length - 1; i++) {
      const u = finalPath[i];
      const v = finalPath[i + 1];
      const edge = edges.find(
        e => (e.source === u && e.target === v) || (e.source === v && e.target === u)
      );
      if (edge) totalCost += edge.weight;
    }
  }

  return {
    path: finalPath,
    visitedOrder,
    visitedNodes: Array.from(visitedSet),
    totalCost,
    totalHops: finalPath.length > 0 ? finalPath.length - 1 : 0,
    executionTimeMs: parseFloat((endTime - startTime).toFixed(4)),
    steps
  };
}

// BFS implementation with telemetry recording
export function runBFS(
  nodes: Node[],
  edges: Edge[],
  sourceId: string,
  destinationId: string
): SimulationResult {
  const startTime = performance.now();
  const adj = buildAdjacencyList(nodes, edges);

  const visitedOrder: string[] = [];
  const steps: TraversalStep[] = [];
  const visitedSet = new Set<string>();
  
  const parentMap: Record<string, string> = {};
  const queue: { current: string; parent: string | null; path: string[] }[] = [];

  let finalPath: string[] = [];
  let found = false;

  if (nodes.some(n => n.id === sourceId)) {
    queue.push({ current: sourceId, parent: null, path: [] });
    visitedSet.add(sourceId);
  }

  while (queue.length > 0) {
    const { current, parent, path } = queue.shift()!;
    visitedOrder.push(current);

    steps.push({
      nodeId: current,
      action: current === destinationId ? 'found' : 'visit',
      parentId: parent,
      pathSoFar: [...path, current]
    });

    if (current === destinationId) {
      found = true;
      finalPath = [...path, current];
      break;
    }

    const neighbors = adj[current] || [];
    for (const neighbor of neighbors) {
      if (!visitedSet.has(neighbor.target)) {
        visitedSet.add(neighbor.target);
        parentMap[neighbor.target] = current;
        queue.push({
          current: neighbor.target,
          parent: current,
          path: [...path, current]
        });
      }
    }
  }

  const endTime = performance.now();

  // Calculate path cost
  let totalCost = 0;
  if (finalPath.length > 0) {
    for (let i = 0; i < finalPath.length - 1; i++) {
      const u = finalPath[i];
      const v = finalPath[i + 1];
      const edge = edges.find(
        e => (e.source === u && e.target === v) || (e.source === v && e.target === u)
      );
      if (edge) totalCost += edge.weight;
    }
  }

  return {
    path: finalPath,
    visitedOrder,
    visitedNodes: Array.from(visitedSet),
    totalCost,
    totalHops: finalPath.length > 0 ? finalPath.length - 1 : 0,
    executionTimeMs: parseFloat((endTime - startTime).toFixed(4)),
    steps
  };
}

// Generate a professional standard sample networking graph
export function generateDefaultGraph(): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [
    { id: 'N1', name: 'Server A', x: 120, y: 150 },
    { id: 'N2', name: 'Router 1', x: 280, y: 100 },
    { id: 'N3', name: 'Router 2', x: 280, y: 260 },
    { id: 'N4', name: 'Router 3', x: 460, y: 100 },
    { id: 'N5', name: 'Router 4', x: 460, y: 260 },
    { id: 'N6', name: 'Switch B', x: 620, y: 180 },
    { id: 'N7', name: 'Server B', x: 760, y: 180 }
  ];

  const edges: Edge[] = [
    { source: 'N1', target: 'N2', weight: 4 },
    { source: 'N1', target: 'N3', weight: 8 },
    { source: 'N2', target: 'N3', weight: 3 },
    { source: 'N2', target: 'N4', weight: 10 },
    { source: 'N3', target: 'N5', weight: 2 },
    { source: 'N4', target: 'N5', weight: 5 },
    { source: 'N4', target: 'N6', weight: 4 },
    { source: 'N5', target: 'N6', weight: 7 },
    { source: 'N6', target: 'N7', weight: 1 }
  ];

  return { nodes, edges };
}

// Generate a random high-fidelity graph
export function generateRandomGraph(): { nodes: Node[]; edges: Edge[] } {
  const names = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta'];
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  
  const width = 800;
  const height = 360;

  // Position nodes nicely in columns/layers to ensure a clean networking structure
  const cols = 4;
  const nodesPerCol = [1, 2, 2, 1]; // layout: 1 source, layers of routers, 1 destination
  let nameIndex = 0;

  for (let c = 0; c < cols; c++) {
    const numNodes = nodesPerCol[c];
    const x = 100 + c * 200;
    
    for (let r = 0; r < numNodes; r++) {
      const y = height / (numNodes + 1) * (r + 1);
      const id = `R${nameIndex + 1}`;
      const name = names[nameIndex] || `Node ${nameIndex + 1}`;
      nodes.push({ id, name, x, y });
      nameIndex++;
    }
  }

  // Connect nodes across adjacent columns to ensure connectivity and structured flow
  for (let c = 0; c < cols - 1; c++) {
    const currentLayer = nodes.filter((_, idx) => {
      let accum = 0;
      for (let i = 0; i < c; i++) accum += nodesPerCol[i];
      return idx >= accum && idx < accum + nodesPerCol[c];
    });

    const nextLayer = nodes.filter((_, idx) => {
      let accum = 0;
      for (let i = 0; i <= c; i++) accum += nodesPerCol[i];
      return idx >= accum && idx < accum + nodesPerCol[c + 1];
    });

    currentLayer.forEach(u => {
      nextLayer.forEach(v => {
        // High probability of connection
        if (Math.random() > 0.1) {
          edges.push({
            source: u.id,
            target: v.id,
            weight: Math.floor(Math.random() * 9) + 2 // weight 2 to 10
          });
        }
      });
    });
  }

  // Ensure there are no disconnected components by adding random intra-layer edges if needed
  // For simplicity, connect Layer 1 router 1 & router 2
  if (nodesPerCol[1] === 2) {
    edges.push({ source: 'R2', target: 'R3', weight: Math.floor(Math.random() * 5) + 2 });
  }
  if (nodesPerCol[2] === 2) {
    edges.push({ source: 'R4', target: 'R5', weight: Math.floor(Math.random() * 5) + 2 });
  }

  return { nodes, edges };
}
