from collections import deque
from network import Graph


def bfs(graph: Graph, src: str, dst: str) -> dict:
    src, dst = src.strip().upper(), dst.strip().upper()
    if src not in graph.nodes or dst not in graph.nodes:
        return {"success": False, "msg": "Source or Destination does not exist.", "steps": [], "path": []}
    if not graph.nodes[src]["online"] or not graph.nodes[dst]["online"]:
        return {"success": False, "msg": "Source or Destination router is offline.", "steps": [], "path": []}

    steps = []
    if src == dst:
        steps.append({"step": 1, "type": "COMPLETE", "node": src, "structure": [src], "visited": [src], "parents": {src: None}, "edge": None, "msg": f"Source is destination (0 hops)."})
        return {"algo": "BFS (Queue)", "success": True, "path": [src], "hops": 0, "steps": steps, "visited": [src], "parents": {src: None}, "tree_edges": [], "max_structure": 1, "msg": "Direct match."}

    queue = deque([src])
    visited = {src}
    parents = {src: None}
    visited_order = []
    tree_edges = []
    max_q = 1

    steps.append({"step": 1, "type": "ENQUEUE", "node": src, "structure": list(queue), "visited": [], "parents": dict(parents), "edge": None, "msg": f"Enqueued source {src} into FIFO queue (Front/Rear)."})

    found = False
    while queue:
        curr = queue.popleft()
        visited_order.append(curr)

        steps.append({"step": len(steps) + 1, "type": "DEQUEUE", "node": curr, "structure": list(queue), "visited": list(visited_order), "parents": dict(parents), "edge": None, "msg": f"Dequeued {curr} from queue front to explore neighbors."})

        if curr == dst:
            found = True
            break

        for nbr in sorted(graph.adj.get(curr, [])):
            if not graph.nodes[nbr]["online"]:
                continue
            if nbr not in visited:
                visited.add(nbr)
                parents[nbr] = curr
                tree_edges.append((curr, nbr))
                queue.append(nbr)
                max_q = max(max_q, len(queue))

                steps.append({"step": len(steps) + 1, "type": "ENQUEUE", "node": nbr, "structure": list(queue), "visited": list(visited_order), "parents": dict(parents), "edge": (curr, nbr), "msg": f"Discovered {nbr} via link ({curr}-{nbr}). Added to queue rear."})

                if nbr == dst:
                    found = True
                    visited_order.append(nbr)
                    steps.append({"step": len(steps) + 1, "type": "FOUND", "node": nbr, "structure": list(queue), "visited": list(visited_order), "parents": dict(parents), "edge": (curr, nbr), "msg": f"Destination {dst} discovered! BFS guarantees shortest-hop route."})
                    break
        if found:
            break

    if not found:
        steps.append({"step": len(steps) + 1, "type": "FAILED", "node": None, "structure": list(queue), "visited": list(visited_order), "parents": dict(parents), "edge": None, "msg": f"Queue empty. No reachable route to {dst}."})
        return {"algo": "BFS (Queue)", "success": False, "path": [], "hops": 0, "steps": steps, "visited": visited_order, "parents": parents, "tree_edges": tree_edges, "max_structure": max_q, "msg": f"No path found to {dst}."}

    path = []
    curr_back = dst
    while curr_back is not None:
        path.append(curr_back)
        curr_back = parents.get(curr_back)
    path.reverse()

    steps.append({"step": len(steps) + 1, "type": "COMPLETE", "node": dst, "structure": list(queue), "visited": list(visited_order), "parents": dict(parents), "edge": None, "msg": f"Shortest route reconstructed: {' -> '.join(path)} ({len(path) - 1} hops)."})
    return {"algo": "BFS (Queue)", "success": True, "path": path, "hops": len(path) - 1, "steps": steps, "visited": visited_order, "parents": parents, "tree_edges": tree_edges, "max_structure": max_q, "msg": f"Shortest Route: {' -> '.join(path)}"}


def dfs(graph: Graph, src: str, dst: str) -> dict:
    src, dst = src.strip().upper(), dst.strip().upper()
    if src not in graph.nodes or dst not in graph.nodes:
        return {"success": False, "msg": "Source or Destination does not exist.", "steps": [], "path": []}
    if not graph.nodes[src]["online"] or not graph.nodes[dst]["online"]:
        return {"success": False, "msg": "Source or Destination router is offline.", "steps": [], "path": []}

    steps = []
    if src == dst:
        steps.append({"step": 1, "type": "COMPLETE", "node": src, "structure": [src], "visited": [src], "parents": {src: None}, "edge": None, "msg": f"Source is destination (0 hops)."})
        return {"algo": "DFS (Stack)", "success": True, "path": [src], "hops": 0, "steps": steps, "visited": [src], "parents": {src: None}, "tree_edges": [], "max_structure": 1, "msg": "Direct match."}

    stack = [(src, [src])]
    visited = set()
    visited_order = []
    parents = {src: None}
    tree_edges = []
    max_s = 1

    steps.append({"step": 1, "type": "PUSH", "node": src, "structure": [s[0] for s in stack], "visited": [], "parents": dict(parents), "edge": None, "msg": f"Pushed source {src} onto LIFO stack top."})

    found_path = None
    while stack:
        curr, path = stack.pop()

        if curr in visited:
            continue
        visited.add(curr)
        visited_order.append(curr)

        steps.append({"step": len(steps) + 1, "type": "POP", "node": curr, "structure": [s[0] for s in stack], "visited": list(visited_order), "parents": dict(parents), "edge": None, "msg": f"Popped {curr} from stack top to explore deep branch."})

        if curr == dst:
            found_path = path
            steps.append({"step": len(steps) + 1, "type": "FOUND", "node": curr, "structure": [s[0] for s in stack], "visited": list(visited_order), "parents": dict(parents), "edge": None, "msg": f"Destination {dst} discovered via DFS!"})
            break

        nbrs = [n for n in sorted(graph.adj.get(curr, []), reverse=True) if graph.nodes[n]["online"] and n not in visited]
        if nbrs:
            for nbr in nbrs:
                parents[nbr] = curr
                tree_edges.append((curr, nbr))
                stack.append((nbr, path + [nbr]))
                max_s = max(max_s, len(stack))
                steps.append({"step": len(steps) + 1, "type": "PUSH", "node": nbr, "structure": [s[0] for s in stack], "visited": list(visited_order), "parents": dict(parents), "edge": (curr, nbr), "msg": f"Pushed unvisited neighbor {nbr} onto stack top."})
        elif stack:
            steps.append({"step": len(steps) + 1, "type": "BACKTRACK", "node": curr, "structure": [s[0] for s in stack], "visited": list(visited_order), "parents": dict(parents), "edge": None, "msg": f"Dead end at {curr}. Backtracking to next node on stack."})

    if not found_path:
        steps.append({"step": len(steps) + 1, "type": "FAILED", "node": None, "structure": [s[0] for s in stack], "visited": list(visited_order), "parents": dict(parents), "edge": None, "msg": f"Stack empty. No path found to {dst}."})
        return {"algo": "DFS (Stack)", "success": False, "path": [], "hops": 0, "steps": steps, "visited": visited_order, "parents": parents, "tree_edges": tree_edges, "max_structure": max_s, "msg": f"No path found to {dst}."}

    steps.append({"step": len(steps) + 1, "type": "COMPLETE", "node": dst, "structure": [s[0] for s in stack], "visited": list(visited_order), "parents": dict(parents), "edge": None, "msg": f"DFS Route found: {' -> '.join(found_path)} ({len(found_path) - 1} hops)."})
    return {"algo": "DFS (Stack)", "success": True, "path": found_path, "hops": len(found_path) - 1, "steps": steps, "visited": visited_order, "parents": parents, "tree_edges": tree_edges, "max_structure": max_s, "msg": f"DFS Route: {' -> '.join(found_path)}"}
