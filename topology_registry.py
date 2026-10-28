import os
import json
from typing import Dict, List, Any, Optional, Tuple
from network import Graph, validate_topology_dict
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PRESET_KEY_MAPPING = {'reference_network.json': 'reference', 'sample_network.json': 'mesh', 'ring_network.json': 'ring', 'disconnected_network.json': 'disconnected', 'direct_network.json': 'direct', 'multi_route_network.json': 'multi_route', 'offline_router_network.json': 'offline_router'}

class TopologyRegistry:

    def __init__(self, data_dir: str=DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.refresh()

    def refresh(self) -> Dict[str, Dict[str, Any]]:
        self._cache.clear()
        if not os.path.isdir(self.data_dir):
            return self._cache
        priority_keys = ['reference', 'mesh', 'ring', 'disconnected', 'direct', 'multi_route', 'offline_router']
        discovered: Dict[str, Dict[str, Any]] = {}
        for filename in sorted(os.listdir(self.data_dir)):
            if not filename.endswith('.json'):
                continue
            filepath = os.path.join(self.data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        continue
                    data = json.loads(content)
                valid, err_msg, cleaned_data = validate_topology_dict(data)
                if not valid or cleaned_data is None:
                    continue
                preset_key = PRESET_KEY_MAPPING.get(filename, os.path.splitext(filename)[0].lower())
                name = cleaned_data.get('name') or preset_key.replace('_', ' ').title()
                desc = cleaned_data.get('description', f"{len(cleaned_data['routers'])} routers, {len(cleaned_data['edges'])} links.")
                discovered[preset_key] = {'id': preset_key, 'filename': filename, 'filepath': filepath, 'name': name, 'description': desc, 'router_count': len(cleaned_data['routers']), 'edge_count': len(cleaned_data['edges']), 'data': cleaned_data}
            except Exception:
                continue
        for pk in priority_keys:
            if pk in discovered:
                self._cache[pk] = discovered[pk]
        for k, v in discovered.items():
            if k not in self._cache:
                self._cache[k] = v
        return self._cache

    def get_available_presets(self) -> Dict[str, Dict[str, Any]]:
        if not self._cache:
            self.refresh()
        return self._cache

    def get_preset_options(self) -> Dict[str, str]:
        presets = self.get_available_presets()
        return {pid: meta['name'] for pid, meta in presets.items()}

    def load_graph(self, preset_key: str) -> Optional[Graph]:
        presets = self.get_available_presets()
        normalized_key = preset_key.strip().lower()
        if normalized_key in ('sample', 'full_mesh'):
            normalized_key = 'mesh'
        elif normalized_key == 'default':
            normalized_key = 'reference'
        meta = presets.get(normalized_key)
        if not meta:
            if 'reference' in presets:
                meta = presets['reference']
            elif presets:
                meta = next(iter(presets.values()))
            else:
                return None
        g = Graph()
        ok, _ = g.load_from_dict(meta['data'])
        if ok:
            g.name = meta['name']
            return g
        return None
_registry = TopologyRegistry()

def get_topology_registry(data_dir: str=DEFAULT_DATA_DIR) -> TopologyRegistry:
    global _registry
    if _registry.data_dir != data_dir:
        _registry = TopologyRegistry(data_dir)
    return _registry
