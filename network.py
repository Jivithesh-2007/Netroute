import math
import os
import json
from collections import deque
from typing import Dict, List, Set, Tuple, Optional, Any

class Router:

    def __init__(self, router_id: str, name: str='', x: float=200.0, y: float=200.0, is_online: bool=True):
        self.id = router_id.strip().upper()
        self.name = name.strip() or f'Router {self.id}'
        self.x = float(x)
        self.y = float(y)
        self.is_online = bool(is_online)

    def to_dict(self) -> Dict[str, Any]:
        return {'id': self.id, 'name': self.name, 'x': self.x, 'y': self.y, 'is_online': self.is_online}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Router':
        return cls(router_id=data['id'], name=data.get('name', ''), x=data.get('x', 200.0), y=data.get('y', 200.0), is_online=data.get('is_online', True))

class Graph:

    def __init__(self, name: str=''):
        self.name: str = name
        self.routers: Dict[str, Router] = {}
        self.adjacency: Dict[str, List[str]] = {}
        self.weights: Dict[Tuple[str, str], float] = {}
        self.failed_edges: Set[Tuple[str, str]] = set()

    def add_router(self, router_id: str, name: str='', x: float=200.0, y: float=200.0, is_online: bool=True) -> bool:
        valid, _ = validate_router_id(router_id)
        if not valid:
            return False
        rid = router_id.strip().upper()
        if rid in self.routers:
            return False
        self.routers[rid] = Router(rid, name, x, y, is_online)
        self.adjacency[rid] = []
        return True

    def remove_router(self, router_id: str) -> bool:
        rid = router_id.strip().upper()
        if rid not in self.routers:
            return False
        del self.routers[rid]
        del self.adjacency[rid]
        for u in self.adjacency:
            self.adjacency[u] = [v for v in self.adjacency[u] if v != rid]
        self.weights = {k: w for k, w in self.weights.items() if rid not in k}
        self.failed_edges = {k for k in self.failed_edges if rid not in k}
        return True

    def rename_router(self, router_id: str, new_name: str) -> bool:
        rid = router_id.strip().upper()
        if rid in self.routers and new_name.strip():
            self.routers[rid].name = new_name.strip()
            return True
        return False

    def auto_layout(self):
        nodes = sorted(self.routers.keys())
        n = len(nodes)
        if n == 0:
            return
        cx, cy = (360.0, 210.0)
        radius = min(220.0, max(100.0, 28.0 * n))
        for i, rid in enumerate(nodes):
            angle = 2 * math.pi * i / n - math.pi / 2
            self.routers[rid].x = round(cx + radius * math.cos(angle), 1)
            self.routers[rid].y = round(cy + radius * math.sin(angle), 1)

    def add_connection(self, u: str, v: str, weight: float=1.0) -> bool:
        u_id, v_id = (u.strip().upper(), v.strip().upper())
        if u_id not in self.routers or v_id not in self.routers or u_id == v_id:
            return False
        if v_id in self.adjacency[u_id]:
            return False
        if weight < 0:
            return False
        self.adjacency[u_id].append(v_id)
        self.adjacency[v_id].append(u_id)
        pair = tuple(sorted((u_id, v_id)))
        self.weights[pair] = float(weight)
        return True

    def remove_connection(self, u: str, v: str) -> bool:
        u_id, v_id = (u.strip().upper(), v.strip().upper())
        if u_id in self.adjacency and v_id in self.adjacency[u_id]:
            self.adjacency[u_id].remove(v_id)
            self.adjacency[v_id].remove(u_id)
            pair = tuple(sorted((u_id, v_id)))
            self.weights.pop(pair, None)
            self.failed_edges.discard(pair)
            return True
        return False

    def get_neighbors(self, router_id: str) -> List[str]:
        rid = router_id.strip().upper()
        return sorted(self.adjacency.get(rid, []))

    def get_weight(self, u: str, v: str) -> float:
        pair = tuple(sorted((u.strip().upper(), v.strip().upper())))
        return self.weights.get(pair, 1.0)

    def set_weight(self, u: str, v: str, weight: float) -> bool:
        if weight < 0:
            return False
        u_id, v_id = (u.strip().upper(), v.strip().upper())
        if u_id not in self.routers or v_id not in self.routers:
            return False
        pair = tuple(sorted((u_id, v_id)))
        if v_id not in self.adjacency.get(u_id, []):
            return False
        self.weights[pair] = float(weight)
        return True

    def toggle_edge_failure(self, u: str, v: str) -> Optional[bool]:
        u_id, v_id = (u.strip().upper(), v.strip().upper())
        if u_id not in self.routers or v_id not in self.routers:
            return None
        pair = tuple(sorted((u_id, v_id)))
        if v_id not in self.adjacency.get(u_id, []):
            return None
        if pair in self.failed_edges:
            self.failed_edges.remove(pair)
            return True
        else:
            self.failed_edges.add(pair)
            return False

    def is_edge_active(self, u: str, v: str) -> bool:
        pair = tuple(sorted((u.strip().upper(), v.strip().upper())))
        return pair not in self.failed_edges

    def toggle_router_status(self, router_id: str) -> Optional[bool]:
        rid = router_id.strip().upper()
        if rid in self.routers:
            self.routers[rid].is_online = not self.routers[rid].is_online
            return self.routers[rid].is_online
        return None

    def set_router_status(self, router_id: str, is_online: bool) -> bool:
        rid = router_id.strip().upper()
        if rid in self.routers:
            self.routers[rid].is_online = bool(is_online)
            return True
        return False

    def get_edges(self) -> List[Tuple[str, str]]:
        edge_set = set()
        for u, neighbors in self.adjacency.items():
            for v in neighbors:
                edge_set.add(tuple(sorted((u, v))))
        return sorted(list(edge_set))

    def get_adjacency_list(self) -> Dict[str, List[str]]:
        return {r: sorted(self.adjacency[r]) for r in sorted(self.routers.keys())}

    def get_adjacency_matrix(self) -> Tuple[List[str], List[List[int]]]:
        nodes = sorted(self.routers.keys())
        idx_map = {r: i for i, r in enumerate(nodes)}
        n = len(nodes)
        matrix = [[0] * n for _ in range(n)]
        for u, neighbors in self.adjacency.items():
            for v in neighbors:
                if u in idx_map and v in idx_map:
                    matrix[idx_map[u]][idx_map[v]] = 1
        return (nodes, matrix)

    def get_connected_components(self) -> List[Set[str]]:
        visited = set()
        components = []
        for rid, router in sorted(self.routers.items()):
            if not router.is_online or rid in visited:
                continue
            comp = set()
            queue = deque([rid])
            visited.add(rid)
            while queue:
                curr = queue.popleft()
                comp.add(curr)
                for nbr in self.adjacency.get(curr, []):
                    if nbr in self.routers and self.routers[nbr].is_online and self.is_edge_active(curr, nbr) and (nbr not in visited):
                        visited.add(nbr)
                        queue.append(nbr)
            components.append(comp)
        return components

    def is_connected(self) -> bool:
        online_count = sum((1 for r in self.routers.values() if r.is_online))
        if online_count <= 1:
            return True
        comps = self.get_connected_components()
        return len(comps) == 1 and len(comps[0]) == online_count

    def is_reachable(self, src: str, dst: str) -> bool:
        src, dst = (src.strip().upper(), dst.strip().upper())
        if src not in self.routers or dst not in self.routers:
            return False
        if not self.routers[src].is_online or not self.routers[dst].is_online:
            return False
        if src == dst:
            return True
        visited = {src}
        queue = deque([src])
        while queue:
            curr = queue.popleft()
            if curr == dst:
                return True
            for nbr in self.adjacency.get(curr, []):
                if nbr in self.routers and self.routers[nbr].is_online and self.is_edge_active(curr, nbr) and (nbr not in visited):
                    visited.add(nbr)
                    queue.append(nbr)
        return False

    def get_reachable_nodes(self, src: str) -> List[str]:
        src_clean = src.strip().upper()
        if src_clean not in self.routers or not self.routers[src_clean].is_online:
            return []
        visited = {src_clean}
        queue = deque([src_clean])
        while queue:
            curr = queue.popleft()
            for nbr in self.adjacency.get(curr, []):
                if nbr in self.routers and self.routers[nbr].is_online and self.is_edge_active(curr, nbr) and (nbr not in visited):
                    visited.add(nbr)
                    queue.append(nbr)
        return sorted(list(visited))

    def generate_routing_table(self, source_id: str) -> List[Dict[str, Any]]:
        src = source_id.strip().upper()
        if src not in self.routers or not self.routers[src].is_online:
            table: List[Dict[str, Any]] = []
            for dest in sorted(self.routers.keys()):
                table.append({'destination': dest, 'next_hop': 'None', 'hops': -1, 'status': 'Source Offline' if src in self.routers else 'Source Not Found'})
            return table
        parents: Dict[str, Optional[str]] = {src: None}
        queue = deque([src])
        visited = {src}
        while queue:
            curr = queue.popleft()
            for nbr in sorted(self.adjacency.get(curr, [])):
                if nbr in self.routers and self.routers[nbr].is_online and self.is_edge_active(curr, nbr) and (nbr not in visited):
                    visited.add(nbr)
                    parents[nbr] = curr
                    queue.append(nbr)
        table = []
        for dest in sorted(self.routers.keys()):
            if dest == src:
                table.append({'destination': dest, 'next_hop': src, 'hops': 0, 'status': 'Local (Self)'})
            elif dest in parents:
                path: List[str] = []
                curr_node: Optional[str] = dest
                while curr_node is not None:
                    path.append(curr_node)
                    curr_node = parents.get(curr_node)
                path.reverse()
                next_hop = path[1] if len(path) > 1 else dest
                hops = len(path) - 1
                status = 'Direct Neighbor' if hops == 1 else 'Reachable'
                table.append({'destination': dest, 'next_hop': next_hop, 'hops': hops, 'status': status})
            else:
                table.append({'destination': dest, 'next_hop': 'None', 'hops': -1, 'status': 'Unreachable'})
        return table

    def clear(self):
        self.routers.clear()
        self.adjacency.clear()
        self.weights.clear()
        self.failed_edges.clear()

    @classmethod
    def from_preset(cls, preset_name: str) -> 'Graph':
        g = cls()
        g.load_preset(preset_name)
        return g

    def load_preset(self, preset_name: str):
        self.clear()
        p = preset_name.lower().strip()
        if p in ('reference', 'default'):
            ref_file = os.path.join(os.path.dirname(__file__), 'data', 'reference_network.json')
            if os.path.exists(ref_file):
                try:
                    with open(ref_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    ok, _ = self.load_from_dict(data)
                    if ok:
                        return
                except Exception:
                    pass
            nodes = [('N1', 'Server A (Src)', 100.0, 220.0), ('N2', 'Router 1', 230.0, 140.0), ('N3', 'Router 2', 230.0, 300.0), ('N4', 'Router 3', 380.0, 140.0), ('N5', 'Router 4', 380.0, 300.0), ('N6', 'Switch B', 510.0, 220.0), ('N7', 'Server B (Dst)', 630.0, 220.0)]
            for rid, name, x, y in nodes:
                self.add_router(rid, name=name, x=x, y=y)
            links = [('N1', 'N2', 4.0), ('N1', 'N3', 8.0), ('N2', 'N3', 3.0), ('N2', 'N4', 10.0), ('N3', 'N5', 2.0), ('N4', 'N5', 5.0), ('N4', 'N6', 4.0), ('N5', 'N6', 7.0), ('N6', 'N7', 1.0)]
            for u, v, w in links:
                self.add_connection(u, v, weight=w)
        elif p in ('ring', 'cyclic'):
            cx, cy, r = (360.0, 210.0, 140.0)
            for i in range(6):
                rid = f'R{i + 1}'
                angle = 2 * math.pi * i / 6 - math.pi / 2
                x = round(cx + r * math.cos(angle), 1)
                y = round(cy + r * math.sin(angle), 1)
                self.add_router(rid, name=f'Node {rid}', x=x, y=y)
            ring_links = [('R1', 'R2'), ('R2', 'R3'), ('R3', 'R4'), ('R4', 'R5'), ('R5', 'R6'), ('R6', 'R1')]
            for u, v in ring_links:
                self.add_connection(u, v, weight=1.0)
        elif p in ('mesh', 'sample', 'full_mesh'):
            sample_file = os.path.join(os.path.dirname(__file__), 'data', 'sample_network.json')
            if os.path.exists(sample_file):
                try:
                    with open(sample_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    ok, _ = self.load_from_dict(data)
                    if ok:
                        return
                except Exception:
                    pass
            nodes = [('R1', 'Router R1', 120.0, 120.0), ('R2', 'Router R2', 320.0, 80.0), ('R3', 'Router R3', 520.0, 140.0), ('R4', 'Router R4', 180.0, 300.0), ('R5', 'Router R5', 380.0, 320.0), ('R6', 'Router R6', 580.0, 300.0)]
            for rid, name, x, y in nodes:
                self.add_router(rid, name=name, x=x, y=y)
            mesh_links = [('R1', 'R2'), ('R1', 'R4'), ('R2', 'R3'), ('R2', 'R5'), ('R3', 'R6'), ('R4', 'R5'), ('R5', 'R6'), ('R2', 'R4')]
            for u, v in mesh_links:
                self.add_connection(u, v, weight=1.0)
        elif p == 'disconnected':
            nodes = [('R1', 'Subnet A (R1)', 140.0, 130.0), ('R2', 'Subnet A (R2)', 260.0, 90.0), ('R3', 'Subnet A (R3)', 200.0, 270.0), ('R4', 'Subnet B (R4)', 440.0, 130.0), ('R5', 'Subnet B (R5)', 560.0, 90.0), ('R6', 'Subnet B (R6)', 500.0, 270.0)]
            for rid, name, x, y in nodes:
                self.add_router(rid, name=name, x=x, y=y)
            for u, v in [('R1', 'R2'), ('R2', 'R3'), ('R1', 'R3'), ('R4', 'R5'), ('R5', 'R6'), ('R4', 'R6')]:
                self.add_connection(u, v, weight=1.0)
        elif p == 'direct':
            nodes = [('R1', 120.0, 200.0), ('R2', 260.0, 200.0), ('R3', 400.0, 200.0), ('R4', 540.0, 200.0)]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y)
            for u, v in [('R1', 'R2'), ('R2', 'R3'), ('R3', 'R4')]:
                self.add_connection(u, v, weight=1.0)
        elif p == 'multi_route':
            nodes = [('R1', 100.0, 180.0), ('R2', 260.0, 90.0), ('R3', 420.0, 90.0), ('R4', 220.0, 270.0), ('R5', 340.0, 270.0), ('R6', 460.0, 270.0), ('R7', 580.0, 180.0)]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y)
            links = [('R1', 'R2'), ('R2', 'R3'), ('R3', 'R7'), ('R1', 'R4'), ('R4', 'R5'), ('R5', 'R6'), ('R6', 'R7')]
            for u, v in links:
                self.add_connection(u, v, weight=1.0)
        elif p == 'offline_router':
            nodes = [('R1', 120.0, 180.0), ('R2', 280.0, 120.0), ('R3', 440.0, 180.0), ('R4', 280.0, 250.0), ('R5', 560.0, 180.0)]
            for rid, x, y in nodes:
                self.add_router(rid, x=x, y=y, is_online=rid != 'R2')
            for u, v in [('R1', 'R2'), ('R2', 'R3'), ('R1', 'R4'), ('R4', 'R3'), ('R3', 'R5')]:
                self.add_connection(u, v, weight=1.0)
        else:
            self.load_preset('reference')

    def get_summary(self) -> Dict[str, Any]:
        online_count = sum((1 for r in self.routers.values() if r.is_online))
        comps = self.get_connected_components()
        return {'total_routers': len(self.routers), 'online_routers': online_count, 'offline_routers': len(self.routers) - online_count, 'total_edges': len(self.get_edges()), 'is_connected': self.is_connected(), 'component_count': len(comps), 'components': [sorted(list(c)) for c in comps]}

    def to_dict(self) -> Dict[str, Any]:
        return {'directed': False, 'name': self.name or 'Custom Topology', 'routers': [r.to_dict() for r in self.routers.values()], 'edges': [[u, v, self.get_weight(u, v)] for u, v in self.get_edges()], 'failed_edges': [list(e) for e in sorted(self.failed_edges)]}

    def clone(self) -> 'Graph':
        g = Graph(name=self.name)
        g.load_from_dict(self.to_dict())
        return g

    def load_from_dict(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        valid, err_msg, cleaned = validate_topology_dict(data)
        if not valid or cleaned is None:
            return (False, f'Failed to load topology: {err_msg}')
        self.clear()
        self.name = cleaned.get('name', 'Active Topology')
        for rdata in cleaned['routers']:
            self.add_router(router_id=rdata['id'], name=rdata['name'], x=rdata['x'], y=rdata['y'], is_online=rdata['is_online'])
        for edge in cleaned['edges']:
            self.add_connection(edge[0], edge[1], weight=edge[2])
        for fe in cleaned['failed_edges']:
            self.failed_edges.add(tuple(sorted((str(fe[0]), str(fe[1])))))
        return (True, f'Loaded {len(self.routers)} routers and {len(self.get_edges())} connections.')

def validate_router_id(router_id: str) -> Tuple[bool, str]:
    rid = router_id.strip().upper()
    if not rid:
        return (False, 'Router ID cannot be empty.')
    if len(rid) > 8:
        return (False, 'Router ID cannot exceed 8 characters.')
    if not rid.isalnum():
        return (False, 'Router ID must be alphanumeric (e.g., R1, GW2).')
    return (True, rid)

def validate_topology_dict(data: Any) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    if not isinstance(data, dict):
        return (False, 'Topology data must be a JSON object (dictionary).', None)
    if 'routers' not in data or not isinstance(data['routers'], list):
        return (False, "Topology schema violation: missing or invalid 'routers' array.", None)
    if 'edges' not in data or not isinstance(data['edges'], list):
        return (False, "Topology schema violation: missing or invalid 'edges' array.", None)
    seen_ids: Set[str] = set()
    cleaned_routers: List[Dict[str, Any]] = []
    for idx, rdata in enumerate(data['routers']):
        if not isinstance(rdata, dict):
            return (False, f'Router entry #{idx + 1} must be an object.', None)
        raw_id = rdata.get('id')
        if raw_id is None or not str(raw_id).strip():
            return (False, f"Router entry #{idx + 1} is missing required 'id' field.", None)
        valid_id, rid_clean = validate_router_id(str(raw_id))
        if not valid_id:
            return (False, f"Router entry #{idx + 1} has invalid ID '{raw_id}': {rid_clean}", None)
        if rid_clean in seen_ids:
            return (False, f"Duplicate router ID '{rid_clean}' detected in topology.", None)
        seen_ids.add(rid_clean)
        raw_name = rdata.get('name', '')
        router_name = str(raw_name).strip() if raw_name else f'Router {rid_clean}'
        try:
            x_val = float(rdata.get('x', 200.0))
            y_val = float(rdata.get('y', 200.0))
            if not math.isfinite(x_val) or not math.isfinite(y_val):
                raise ValueError('Non-finite coordinates')
        except (ValueError, TypeError):
            return (False, f"Router '{rid_clean}' has invalid coordinates (must be finite numbers).", None)
        is_online = bool(rdata.get('is_online', True))
        cleaned_routers.append({'id': rid_clean, 'name': router_name, 'x': round(x_val, 1), 'y': round(y_val, 1), 'is_online': is_online})
    seen_edges: Set[Tuple[str, str]] = set()
    cleaned_edges: List[List[Any]] = []
    for idx, edge in enumerate(data['edges']):
        if not isinstance(edge, (list, tuple)) or len(edge) < 2:
            return (False, f'Connection #{idx + 1} must be an array of at least 2 router IDs [u, v].', None)
        u = str(edge[0]).strip().upper()
        v = str(edge[1]).strip().upper()
        if u not in seen_ids or v not in seen_ids:
            missing = u if u not in seen_ids else v
            return (False, f"Connection ({u} <-> {v}) references undefined router ID '{missing}'.", None)
        if u == v:
            return (False, f"Unsupported self-link detected: connection from '{u}' to itself is prohibited.", None)
        pair = tuple(sorted((u, v)))
        if pair in seen_edges:
            return (False, f"Duplicate connection detected between '{u}' and '{v}'.", None)
        seen_edges.add(pair)
        raw_weight = edge[2] if len(edge) >= 3 else 1.0
        try:
            weight = float(raw_weight)
            if not math.isfinite(weight) or weight < 0.0:
                raise ValueError('Invalid weight value')
        except (ValueError, TypeError):
            return (False, f"Connection ({u} <-> {v}) has invalid weight '{raw_weight}'. Weight must be a non-negative finite number.", None)
        cleaned_edges.append([pair[0], pair[1], round(weight, 2)])
    cleaned_failed: List[List[str]] = []
    for fe in data.get('failed_edges', []):
        if isinstance(fe, (list, tuple)) and len(fe) >= 2:
            fu = str(fe[0]).strip().upper()
            fv = str(fe[1]).strip().upper()
            fpair = tuple(sorted((fu, fv)))
            if fpair in seen_edges and fpair not in [tuple(e) for e in cleaned_failed]:
                cleaned_failed.append([fpair[0], fpair[1]])
    cleaned: Dict[str, Any] = {'directed': False, 'name': str(data.get('name', 'Custom Topology')).strip(), 'description': str(data.get('description', '')).strip(), 'routers': cleaned_routers, 'edges': cleaned_edges, 'failed_edges': cleaned_failed}
    return (True, 'Valid topology schema.', cleaned)

def export_topology_json(graph: Graph, name: str='') -> str:
    data = graph.to_dict()
    if name:
        data['name'] = name.strip()
    return json.dumps(data, indent=2)

def import_topology_json(json_str: str) -> Tuple[bool, str, Optional[Graph]]:
    if not json_str or not json_str.strip():
        return (False, 'Uploaded file content is empty.', None)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return (False, f'Invalid JSON syntax: {e.msg} (Line {e.lineno}, Col {e.colno}).', None)
    except Exception as e:
        return (False, f'Failed to parse JSON file: {str(e)}', None)
    valid, err_msg, cleaned = validate_topology_dict(data)
    if not valid or cleaned is None:
        return (False, f'Schema validation error: {err_msg}', None)
    candidate = Graph()
    ok, load_msg = candidate.load_from_dict(cleaned)
    if not ok:
        return (False, f'Candidate graph construction error: {load_msg}', None)
    return (True, f'Topology successfully imported: {len(candidate.routers)} routers, {len(candidate.get_edges())} connections.', candidate)