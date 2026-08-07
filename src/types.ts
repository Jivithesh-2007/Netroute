export interface Node {
  id: string;
  name: string;
  x: number;
  y: number;
}

export interface Edge {
  source: string;
  target: string;
  weight: number;
}

export interface TraversalStep {
  nodeId: string;
  action: 'visit' | 'backtrack' | 'found' | 'current';
  parentId: string | null;
  pathSoFar: string[];
}

export interface SimulationResult {
  path: string[];
  visitedOrder: string[];
  visitedNodes: string[];
  totalCost: number;
  totalHops: number;
  executionTimeMs: number;
  steps: TraversalStep[];
}

export interface PacketHeader {
  source: string;
  destination: string;
  protocol: 'IP' | 'TCP' | 'UDP';
  ttl: number;
  payloadSize: string;
}
