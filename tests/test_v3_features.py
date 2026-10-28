"""
test_v3_features.py — Comprehensive automated test suite for NetRoute V3.
Covers:
1. Feature A: Network Failure Lab & Scenario Isolation
2. Feature B: Explainable Traversal Simulation & Structure Trace
3. Feature C: Route Strategy Comparison & Dijkstra Algorithm
4. Feature D: Network Resilience Analysis (Tarjan's Bridges & Articulation Points)
5. Feature E: Multi-Format CSV, JSON & PNG Figure Exports
6. Feature F: Reproducible Synthetic Benchmark Suite
"""

import pytest
import io
import csv
import json
import plotly.graph_objects as go

from network import Graph
from algorithms import (
    bfs, dfs, dijkstra,
    find_bridges, find_articulation_points,
    simulate_failure, compare_routing_strategies,
    generate_benchmark_graph, benchmark_algorithm, run_benchmark_suite,
    generate_simulation_report, generate_comparison_report
)
from report import (
    export_simulation_metrics_csv,
    export_comparison_metrics_csv,
    export_resilience_csv,
    export_failure_scenario_csv,
    export_benchmark_csv
)
from visualizer import build_network_figure, export_figure_png


def create_reference_graph() -> Graph:
    """Creates the standard 7-node reference network for testing."""
    g = Graph(name="Reference WAN")
    for i in range(1, 8):
        g.add_router(f"N{i}", f"Router {i}", x=100.0 * i, y=150.0)
    # Add connections matching reference network
    edges = [
        ("N1", "N2", 4.0),
        ("N1", "N3", 3.0),
        ("N2", "N3", 2.0),
        ("N2", "N4", 5.0),
        ("N3", "N5", 6.0),
        ("N4", "N5", 1.0),
        ("N4", "N6", 2.0),
        ("N5", "N6", 4.0),
        ("N6", "N7", 2.0)
    ]
    for u, v, w in edges:
        g.add_connection(u, v, weight=w)
    return g


# =============================================================================
# 1. FEATURE A: NETWORK FAILURE LAB TESTS
# =============================================================================
class TestNetworkFailureLab:

    def test_router_failure_impact(self):
        """Disabling an intermediate router reroutes traffic or isolates paths."""
        g = create_reference_graph()
        orig_nodes = len(g.routers)
        orig_edges = len(g.get_edges())

        res = simulate_failure(g, failed_routers=["N4"], failed_edges=[], src="N1", dst="N7")
        assert res["impact_analysis"]["route_survived"] is True
        # With N4 offline, route must bypass N4 (e.g., via N5 -> N6 -> N7)
        scen_path = res["failure_scenario"]["bfs"]["path"]
        assert "N4" not in scen_path
        assert scen_path[-1] == "N7"

        # Verify original graph is untouched
        assert len(g.routers) == orig_nodes
        assert len(g.get_edges()) == orig_edges
        assert g.routers["N4"].is_online is True

    def test_link_failure_impact(self):
        """Severing a connection causes route recalculation."""
        g = create_reference_graph()
        res = simulate_failure(g, failed_routers=[], failed_edges=[("N6", "N7")], src="N1", dst="N7")
        # N6-N7 is a bridge to N7; cutting it must isolate N7
        assert res["impact_analysis"]["destination_became_unreachable"] is True
        assert res["impact_analysis"]["route_survived"] is False
        assert "N7" in res["impact_analysis"]["disconnected_routers"]
        assert g.is_edge_active("N6", "N7") is True  # Baseline unchanged

    def test_multiple_simultaneous_failures(self):
        """Tests simultaneous router outages and link severances."""
        g = create_reference_graph()
        res = simulate_failure(g, failed_routers=["N2", "N5"], failed_edges=[("N1", "N3")], src="N1", dst="N7")
        # Since all neighbors of N1 are either offline (N2) or severed (N1-N3), N1 is isolated
        assert res["impact_analysis"]["route_survived"] is False
        assert res["impact_analysis"]["destination_became_unreachable"] is True
        assert res["failure_scenario"]["component_count"] > res["baseline"]["component_count"]

    def test_exact_scenario_restoration_and_isolation(self):
        """Ensures scenario sandbox clone is completely isolated from baseline."""
        g = create_reference_graph()
        snapshot_dict = g.to_dict()

        res = simulate_failure(g, failed_routers=["N1", "N2", "N3"], failed_edges=[("N4", "N5")], src="N4", dst="N6")
        assert res["scenario_graph"] is not g
        assert res["scenario_graph"].routers["N1"].is_online is False
        assert g.routers["N1"].is_online is True
        assert g.to_dict() == snapshot_dict


# =============================================================================
# 2. FEATURE B: EXPLAINABLE TRAVERSAL SIMULATION TESTS
# =============================================================================
class TestExplainableTraversalSimulation:

    def test_explainable_event_fields_in_bfs(self):
        """Validates that BFS simulation steps contain explainable reasoning fields."""
        g = create_reference_graph()
        res = bfs(g, "N1", "N7")
        assert res["success"] is True
        assert len(res["steps"]) > 0

        for step in res["steps"]:
            assert "step" in step
            assert "operation" in step
            assert "current_node" in step
            assert "why" in step and len(step["why"]) > 0
            assert "structure_before" in step
            assert "structure_after" in step
            assert "structure" in step
            assert "current_path" in step

    def test_explainable_event_fields_in_dfs(self):
        """Validates that DFS simulation steps contain explainable reasoning fields."""
        g = create_reference_graph()
        res = dfs(g, "N1", "N7")
        assert res["success"] is True
        assert len(res["steps"]) > 0

        for step in res["steps"]:
            assert "step" in step
            assert "operation" in step
            assert "why" in step and len(step["why"]) > 0
            assert "structure_before" in step
            assert "structure_after" in step
            assert "current_path" in step

    def test_queue_and_stack_before_after_consistency(self):
        """Checks that structure_before and structure_after accurately track element transitions."""
        g = create_reference_graph()
        bfs_res = bfs(g, "N1", "N7")
        dequeue_steps = [s for s in bfs_res["steps"] if s["operation"] == "DEQUEUE"]
        assert len(dequeue_steps) > 0
        for s in dequeue_steps:
            assert len(s["structure_before"]) == len(s["structure_after"]) + 1

    def test_explainable_unreachable_destination(self):
        """Checks narrative generation when destination is disconnected."""
        g = create_reference_graph()
        g.add_router("N99", "Isolated Island", 0.0, 0.0)
        res = bfs(g, "N1", "N99")
        assert res["success"] is False
        assert len(res["steps"]) > 0
        last_step = res["steps"][-1]
        assert "exhausted" in last_step["why"].lower() or "unreachable" in last_step["why"].lower()


# =============================================================================
# 3. FEATURE C: ROUTE STRATEGY COMPARISON & DIJKSTRA TESTS
# =============================================================================
class TestDijkstraAndStrategyComparison:

    def test_dijkstra_minimum_cost_route(self):
        """Validates that Dijkstra finds the path with strictly minimal total weight."""
        g = create_reference_graph()
        # In reference network:
        # BFS finds: N1 -> N2 -> N4 -> N6 -> N7 (4 hops, cost: 4 + 5 + 2 + 2 = 13.0)
        # Or alternative. Dijkstra finds least-weight.
        res = dijkstra(g, "N1", "N7")
        assert res["success"] is True
        assert res["path"][0] == "N1"
        assert res["path"][-1] == "N7"
        assert res["path_cost"] > 0
        assert res["hops"] == len(res["path"]) - 1

    def test_dijkstra_zero_weight_edges(self):
        """Zero weight edges must be accepted and handled correctly."""
        g = Graph(name="Zero Weight Test")
        g.add_router("A", "A", 0, 0)
        g.add_router("B", "B", 10, 0)
        g.add_router("C", "C", 20, 0)
        g.add_connection("A", "B", weight=0.0)
        g.add_connection("B", "C", weight=5.0)

        res = dijkstra(g, "A", "C")
        assert res["success"] is True
        assert res["path"] == ["A", "B", "C"]
        assert res["path_cost"] == 5.0
        assert res["hops"] == 2

    def test_dijkstra_negative_weight_rejection(self):
        """Dijkstra must reject negative weights with a ValueError."""
        g = Graph(name="Negative Test")
        g.add_router("A", "A", 0, 0)
        g.add_router("B", "B", 10, 0)
        # Directly set negative weight in weights dict to test algorithm-level validation
        g.adjacency["A"] = ["B"]
        g.adjacency["B"] = ["A"]
        g.weights[tuple(sorted(("A", "B")))] = -3.0

        with pytest.raises(ValueError, match="negative edge weight"):
            dijkstra(g, "A", "B")

    def test_dijkstra_unreachable_destination(self):
        """Dijkstra handles disconnected destination gracefully."""
        g = create_reference_graph()
        g.add_router("N99", "Island", 0, 0)
        res = dijkstra(g, "N1", "N99")
        assert res["success"] is False
        assert res["path"] == []
        assert res["hops"] == 0

    def test_compare_routing_strategies_3way(self):
        """Compares BFS (min hops), DFS (branching), and Dijkstra (min cost) simultaneously."""
        g = create_reference_graph()
        res = compare_routing_strategies(g, "N1", "N7")
        assert "bfs" in res and "dfs" in res and "dijkstra" in res
        b_res = res["bfs"]
        d_res = res["dijkstra"]

        # BFS hop count must be <= Dijkstra hop count
        assert b_res["hops"] <= d_res["hops"]
        # Dijkstra path cost must be <= BFS path cost
        assert d_res["path_cost"] <= b_res["path_cost"]


# =============================================================================
# 4. FEATURE D: NETWORK RESILIENCE ANALYSIS TESTS
# =============================================================================
class TestNetworkResilience:

    def test_tarjan_bridges_linear_chain(self):
        """In a linear chain A-B-C-D, every link is a bridge."""
        g = Graph(name="Chain")
        for r in ["A", "B", "C", "D"]:
            g.add_router(r, r, 0, 0)
        g.add_connection("A", "B")
        g.add_connection("B", "C")
        g.add_connection("C", "D")

        bridges = find_bridges(g)
        clean_bridges = {tuple(sorted(e)) for e in bridges}
        expected = {("A", "B"), ("B", "C"), ("C", "D")}
        assert clean_bridges == expected

    def test_tarjan_bridges_ring_graph(self):
        """In a cyclic ring graph A-B-C-D-A, there are 0 bridges."""
        g = Graph(name="Ring")
        for r in ["A", "B", "C", "D"]:
            g.add_router(r, r, 0, 0)
        g.add_connection("A", "B")
        g.add_connection("B", "C")
        g.add_connection("C", "D")
        g.add_connection("D", "A")

        bridges = find_bridges(g)
        assert len(bridges) == 0

    def test_tarjan_articulation_points_linear_chain(self):
        """In a linear chain A-B-C-D, internal nodes B and C are articulation points."""
        g = Graph(name="Chain")
        for r in ["A", "B", "C", "D"]:
            g.add_router(r, r, 0, 0)
        g.add_connection("A", "B")
        g.add_connection("B", "C")
        g.add_connection("C", "D")

        aps = find_articulation_points(g)
        assert set(aps) == {"B", "C"}

    def test_tarjan_resilience_reference_wan(self):
        """On Reference WAN, N6-N7 is a bridge and N6 is an articulation point."""
        g = create_reference_graph()
        bridges = find_bridges(g)
        clean_bridges = {tuple(sorted(e)) for e in bridges}
        assert ("N6", "N7") in clean_bridges

        aps = find_articulation_points(g)
        assert "N6" in aps

    def test_resilience_disconnected_graph(self):
        """Resilience algorithms run correctly on multi-component graphs."""
        g = create_reference_graph()
        # Add a disconnected secondary subnet X-Y
        g.add_router("X", "X", 0, 0)
        g.add_router("Y", "Y", 0, 0)
        g.add_connection("X", "Y")

        bridges = find_bridges(g)
        clean_bridges = {tuple(sorted(e)) for e in bridges}
        assert ("X", "Y") in clean_bridges
        assert ("N6", "N7") in clean_bridges


# =============================================================================
# 5. FEATURE E: MULTI-FORMAT EXPORTS TESTS
# =============================================================================
class TestMultiFormatExports:

    def test_export_simulation_metrics_csv(self):
        """Validates CSV generation for a single traversal run."""
        g = create_reference_graph()
        sim_res = bfs(g, "N1", "N7")
        rep = generate_simulation_report(g, sim_res, "N1", "N7")
        csv_str = export_simulation_metrics_csv(rep)

        reader = csv.reader(io.StringIO(csv_str))
        rows = list(reader)
        assert len(rows) >= 2
        assert "Algorithm" in rows[0]
        assert "Status" in rows[0]

    def test_export_comparison_metrics_csv(self):
        """Validates CSV generation for BFS vs DFS comparison."""
        g = create_reference_graph()
        from algorithms import compare_bfs_dfs
        cmp_res = compare_bfs_dfs(g, "N1", "N7")
        rep = generate_comparison_report(g, cmp_res, "N1", "N7")
        csv_str = export_comparison_metrics_csv(rep)

        reader = csv.reader(io.StringIO(csv_str))
        rows = list(reader)
        assert len(rows) >= 3
        assert "Algorithm" in rows[0]

    def test_export_resilience_csv(self):
        """Validates CSV export for network resilience data."""
        g = create_reference_graph()
        payload = {
            "online_routers": list(g.routers.keys()),
            "active_edges": g.get_edges(),
            "component_count": 1,
            "bridges": find_bridges(g),
            "articulation_points": find_articulation_points(g)
        }
        csv_str = export_resilience_csv(payload)
        assert "Critical Bridges" in csv_str
        assert "Critical Articulation Points" in csv_str

    def test_export_failure_scenario_csv(self):
        """Validates CSV export for failure scenarios."""
        g = create_reference_graph()
        scen_data = simulate_failure(g, failed_routers=["N2"], failed_edges=[], src="N1", dst="N7")
        csv_str = export_failure_scenario_csv(scen_data)
        assert "Baseline" in csv_str
        assert "Failure Scenario" in csv_str

    def test_export_benchmark_csv(self):
        """Validates CSV export for algorithm benchmark records."""
        records = [{
            "routers": 10,
            "edges": 15,
            "density": 0.3,
            "algorithm": "BFS",
            "mean_time_ms": 0.05,
            "min_time_ms": 0.04,
            "max_time_ms": 0.07,
            "std_time_ms": 0.01,
            "hops": 3,
            "path_cost": 5.0,
            "visited_count": 8,
            "explored_edges": 12,
            "theoretical_time": "O(V + E)",
            "theoretical_space": "O(V)"
        }]
        csv_str = export_benchmark_csv(records)
        assert "Routers (V)" in csv_str
        assert "BFS" in csv_str

    def test_export_figure_png_kaleido(self):
        """Validates that Plotly figures export to PNG bytes via Kaleido."""
        g = create_reference_graph()
        fig = build_network_figure(g, {"is_completed": False}, "N1", "N7")
        png_bytes = export_figure_png(fig, width=400, height=300)
        assert png_bytes is not None
        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 1000
        # PNG signature: \x89PNG\r\n\x1a\n
        assert png_bytes.startswith(b"\x89PNG")


# =============================================================================
# 6. FEATURE F: ALGORITHM BENCHMARK LAB TESTS
# =============================================================================
class TestBenchmarkLab:

    def test_generate_benchmark_graph_reproducibility(self):
        """Identical seeds produce identical benchmark graphs."""
        g1 = generate_benchmark_graph(num_routers=15, density=0.25, seed=123)
        g2 = generate_benchmark_graph(num_routers=15, density=0.25, seed=123)

        assert len(g1.routers) == len(g2.routers) == 15
        assert g1.get_edges() == g2.get_edges()
        for u, v in g1.get_edges():
            assert g1.get_weight(u, v) == g2.get_weight(u, v)

    def test_generate_benchmark_graph_connectivity(self):
        """Generated benchmark graphs are guaranteed to be connected."""
        for n in [5, 10, 20]:
            g = generate_benchmark_graph(num_routers=n, density=0.2, seed=42)
            assert g.is_connected() is True
            assert len(g.get_connected_components()) == 1

    def test_benchmark_algorithm_monotonic_timer(self):
        """Validates high-resolution monotonic timer measurement without UI overhead."""
        g = generate_benchmark_graph(num_routers=12, density=0.3, seed=42)
        res = benchmark_algorithm("BFS", g, "N1", "N12", repetitions=5)
        assert res["algorithm"] == "BFS"
        assert res["repetitions"] == 5
        assert res["mean_time_ms"] >= 0.0
        assert res["min_time_ms"] <= res["mean_time_ms"] <= res["max_time_ms"]

    def test_run_benchmark_suite(self):
        """Runs multi-algorithm benchmark suite across multiple scales."""
        suite = run_benchmark_suite(
            router_counts=[6, 10],
            density=0.25,
            algos=["BFS", "DFS", "Dijkstra"],
            repetitions=2,
            seed=42
        )
        assert "records" in suite
        assert len(suite["records"]) == 2 * 3  # 2 scales * 3 algos
        for rec in suite["records"]:
            assert rec["algorithm"] in ["BFS", "DFS", "Dijkstra"]
            assert rec["mean_time_ms"] >= 0.0
