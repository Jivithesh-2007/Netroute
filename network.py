"""Module 2: network.py - Graph Data Structure and Routing (BFS & DFS)."""

class Graph:
    def __init__(self):
        self.nodes = {}  # {router_name: (x, y)}
        self.edges = {}  # {router_name: [connected_routers]}

    def add_node(self, name, x=100, y=100):
        name = name.strip().upper()
        if name and name not in self.nodes:
            self.nodes[name] = (x, y)
            self.edges[name] = []
            return True
        return False

    def add_edge(self, u, v):
        u, v = u.strip().upper(), v.strip().upper()
        if u in self.nodes and v in self.nodes and u != v:
            if v not in self.edges[u]:
                self.edges[u].append(v)
            if u not in self.edges[v]:
                self.edges[v].append(u)
            return True
        return False

    def bfs(self, start, goal):
        """Breadth-First Search: Finds shortest path using a Queue."""
        start, goal = start.strip().upper(), goal.strip().upper()
        if start not in self.nodes or goal not in self.nodes:
            return []
        queue = [[start]]
        visited = [start]
        while queue:
            path = queue.pop(0)  # FIFO Queue
            current = path[-1]
            if current == goal:
                return path
            for neighbor in self.edges.get(current, []):
                if neighbor not in visited:
                    visited.append(neighbor)
                    queue.append(path + [neighbor])
        return []

    def dfs(self, start, goal):
        """Depth-First Search: Discovers path using a Stack."""
        start, goal = start.strip().upper(), goal.strip().upper()
        if start not in self.nodes or goal not in self.nodes:
            return []
        stack = [[start]]
        visited = []
        while stack:
            path = stack.pop()  # LIFO Stack
            current = path[-1]
            if current == goal:
                return path
            if current not in visited:
                visited.append(current)
                for neighbor in reversed(self.edges.get(current, [])):
                    if neighbor not in visited:
                        stack.append(path + [neighbor])
        return []

    def load_sample(self):
        """Loads a default 5-router computer network topology."""
        self.nodes.clear()
        self.edges.clear()
        routers = {"R1": (80, 100), "R2": (220, 50), "R3": (360, 100), "R4": (150, 200), "R5": (290, 200)}
        for name, (x, y) in routers.items():
            self.add_node(name, x, y)
        links = [("R1", "R2"), ("R1", "R4"), ("R2", "R3"), ("R2", "R5"), ("R4", "R5"), ("R3", "R5")]
        for u, v in links:
            self.add_edge(u, v)
