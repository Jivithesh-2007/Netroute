import unittest
from unittest.mock import patch, MagicMock
from network import Graph
from algorithms import bfs, dfs, compare_bfs_dfs
import simulation as sim
from visualizer import build_network_figure

class TestAnimatedTraversal(unittest.TestCase):

    def setUp(self):
        self.graph = Graph()
        self.graph.load_preset('campus')

    def test_bfs_trace_correctness(self):
        res = bfs(self.graph, 'N1', 'N7')
        self.assertTrue(res['success'])
        steps = res['steps']
        self.assertGreater(len(steps), 0)
        s1 = steps[0]
        self.assertEqual(s1['operation'], 'ENQUEUE')
        self.assertEqual(s1['current_node'], 'N1')
        self.assertEqual(s1['structure'], ['N1'])
        self.assertEqual(s1['front'], 'N1')
        self.assertEqual(s1['enqueues'], 1)
        self.assertEqual(s1['dequeues'], 0)
        prev_enq = 0
        prev_deq = 0
        for s in steps:
            self.assertGreaterEqual(s.get('enqueues', 0), prev_enq)
            self.assertGreaterEqual(s.get('dequeues', 0), prev_deq)
            prev_enq = s.get('enqueues', 0)
            prev_deq = s.get('dequeues', 0)
            self.assertIn('parents', s)
            self.assertIn('N1', s['parents'])
        final_s = steps[-1]
        self.assertEqual(final_s['operation'], 'COMPLETE')
        self.assertEqual(final_s['current_node'], 'N7')
        self.assertIn('N7', final_s['current_path'])
        self.assertEqual(final_s['current_path'], res['path'])

    def test_dfs_trace_correctness(self):
        res = dfs(self.graph, 'N1', 'N7')
        self.assertTrue(res['success'])
        steps = res['steps']
        self.assertGreater(len(steps), 0)
        s1 = steps[0]
        self.assertEqual(s1['operation'], 'PUSH')
        self.assertEqual(s1['current_node'], 'N1')
        self.assertEqual(s1['structure'], ['N1'])
        self.assertEqual(s1['top'], 'N1')
        self.assertEqual(s1['pushes'], 1)
        self.assertEqual(s1['pops'], 0)
        has_visited_records = False
        for s in steps:
            self.assertIn('parents', s)
            self.assertIn('structure', s)
            if s.get('visited'):
                has_visited_records = True
        self.assertTrue(has_visited_records)
        final_s = steps[-1]
        self.assertEqual(final_s['operation'], 'COMPLETE')
        self.assertEqual(final_s['current_node'], 'N7')
        self.assertEqual(final_s['current_path'], res['path'])

    def test_dual_comparison_execution(self):
        with patch.object(sim, 'st') as mock_st:
            mock_st.session_state = {}
            cmp_res = sim.execute_dual_comparison(self.graph, 'N1', 'N7')
            self.assertIn('bfs', cmp_res)
            self.assertIn('dfs', cmp_res)
            self.assertEqual(mock_st.session_state['cmp_step_idx'], 0)
            self.assertEqual(mock_st.session_state['cmp_res'], cmp_res)
            self.assertTrue(len(cmp_res['bfs']['steps']) > 0)
            self.assertTrue(len(cmp_res['dfs']['steps']) > 0)

    def test_dual_playback_navigation_controls(self):
        cmp_res = compare_bfs_dfs(self.graph, 'N1', 'N7')
        bfs_steps = len(cmp_res['bfs']['steps'])
        dfs_steps = len(cmp_res['dfs']['steps'])
        max_steps = max(bfs_steps, dfs_steps)
        with patch.object(sim, 'st') as mock_st:
            mock_st.session_state = {'cmp_res': cmp_res, 'cmp_step_idx': 0, 'cmp_is_playing': False, 'cmp_is_paused': False}
            sim.cmp_play()
            self.assertTrue(mock_st.session_state['cmp_is_playing'])
            self.assertFalse(mock_st.session_state['cmp_is_paused'])
            sim.cmp_pause()
            self.assertFalse(mock_st.session_state['cmp_is_playing'])
            self.assertTrue(mock_st.session_state['cmp_is_paused'])
            sim.cmp_resume()
            self.assertTrue(mock_st.session_state['cmp_is_playing'])
            self.assertFalse(mock_st.session_state['cmp_is_paused'])
            sim.cmp_step_forward()
            self.assertEqual(mock_st.session_state['cmp_step_idx'], 1)
            self.assertFalse(mock_st.session_state['cmp_is_playing'])
            sim.cmp_step_backward()
            self.assertEqual(mock_st.session_state['cmp_step_idx'], 0)
            sim.cmp_step_backward()
            self.assertEqual(mock_st.session_state['cmp_step_idx'], 0)
            sim.cmp_jump_to_step(5)
            self.assertEqual(mock_st.session_state['cmp_step_idx'], min(5, max_steps - 1))
            sim.cmp_run_to_completion()
            self.assertEqual(mock_st.session_state['cmp_step_idx'], max_steps - 1)
            self.assertFalse(mock_st.session_state['cmp_is_playing'])
            sim.cmp_restart()
            self.assertEqual(mock_st.session_state['cmp_step_idx'], 0)
            self.assertFalse(mock_st.session_state['cmp_is_playing'])
            self.assertFalse(mock_st.session_state['cmp_is_paused'])
            self.assertIn('N1', self.graph.routers)

    def test_unequal_trace_lengths_synchronization(self):
        cmp_res = compare_bfs_dfs(self.graph, 'N1', 'N7')
        bfs_res = cmp_res['bfs']
        dfs_res = cmp_res['dfs']
        bfs_len = len(bfs_res['steps'])
        dfs_len = len(dfs_res['steps'])
        self.assertNotEqual(bfs_len, dfs_len)
        max_steps = max(bfs_len, dfs_len)
        final_idx = max_steps - 1
        bfs_step_idx = min(final_idx, bfs_len - 1)
        dfs_step_idx = min(final_idx, dfs_len - 1)
        bfs_visual = sim.get_step_visual_state(self.graph, bfs_res, bfs_step_idx)
        dfs_visual = sim.get_step_visual_state(self.graph, dfs_res, dfs_step_idx)
        self.assertTrue(bfs_visual['is_completed'])
        self.assertTrue(dfs_visual['is_completed'])
        self.assertEqual(bfs_visual['route_nodes'], set(bfs_res['path']))
        self.assertEqual(dfs_visual['route_nodes'], set(dfs_res['path']))

    def test_visual_state_active_router_and_connection(self):
        res = bfs(self.graph, 'N1', 'N7')
        edge_step_idx = None
        for i, s in enumerate(res['steps']):
            if s.get('active_edge'):
                edge_step_idx = i
                break
        if edge_step_idx is not None:
            v_state = sim.get_step_visual_state(self.graph, res, edge_step_idx)
            self.assertIsNotNone(v_state['active_edge'])
            self.assertIn(v_state['active_node'], self.graph.routers)
            self.assertIn(tuple(sorted(v_state['active_edge'])), v_state['explored_edges'])

    def test_stable_layout_coordinates_across_steps(self):
        res = bfs(self.graph, 'N1', 'N7')
        v0 = sim.get_step_visual_state(self.graph, res, 0)
        v_final = sim.get_step_visual_state(self.graph, res, len(res['steps']) - 1)
        fig0 = build_network_figure(self.graph, v0, 'N1', 'N7')
        fig_final = build_network_figure(self.graph, v_final, 'N1', 'N7')
        self.assertEqual(fig0.layout.xaxis.range, fig_final.layout.xaxis.range)
        self.assertEqual(fig0.layout.yaxis.range, fig_final.layout.yaxis.range)

    def test_source_equals_destination_route(self):
        res_bfs = bfs(self.graph, 'N1', 'N1')
        self.assertTrue(res_bfs['success'])
        self.assertEqual(res_bfs['hops'], 0)
        self.assertEqual(res_bfs['path'], ['N1'])
        res_dfs = dfs(self.graph, 'N1', 'N1')
        self.assertTrue(res_dfs['success'])
        self.assertEqual(res_dfs['hops'], 0)
        self.assertEqual(res_dfs['path'], ['N1'])

    def test_unreachable_destination(self):
        g = Graph()
        g.add_router('N1', 'Router 1', 50, 50)
        g.add_router('N2', 'Router 2', 150, 50)
        g.add_router('N3', 'Router 3', 300, 300)
        g.add_connection('N1', 'N2', 10.0)
        res_bfs = bfs(g, 'N1', 'N3')
        self.assertFalse(res_bfs['success'])
        self.assertEqual(res_bfs['path'], [])
        self.assertIn('N1', res_bfs['visited'])
        self.assertIn('N2', res_bfs['visited'])
        self.assertNotIn('N3', res_bfs['visited'])
        res_dfs = dfs(g, 'N1', 'N3')
        self.assertFalse(res_dfs['success'])
        self.assertEqual(res_dfs['path'], [])

    def test_topology_mutation_invalidates_simulation(self):
        with patch.object(sim, 'st') as mock_st:
            mock_st.session_state = {'sim_res': {'some': 'data'}, 'step_idx': 5, 'is_playing': True, 'cmp_res': {'cmp': 'data'}, 'cmp_step_idx': 4, 'cmp_is_playing': True}
            sim.invalidate_simulation()
            self.assertIsNone(mock_st.session_state['sim_res'])
            self.assertEqual(mock_st.session_state['step_idx'], 0)
            self.assertFalse(mock_st.session_state['is_playing'])
            self.assertIsNone(mock_st.session_state['cmp_res'])
            self.assertEqual(mock_st.session_state['cmp_step_idx'], 0)
            self.assertFalse(mock_st.session_state['cmp_is_playing'])

    def test_generate_simulation_report_keyword_arguments(self):
        from algorithms import generate_simulation_report
        res = bfs(self.graph, 'N1', 'N7')
        rep = generate_simulation_report(self.graph, res, 'N1', 'N7', algo_name='BFS (Custom Label)')
        self.assertEqual(rep['algorithm'], 'BFS (Custom Label)')
        self.assertEqual(rep['endpoints']['source'], 'N1')
        self.assertEqual(rep['endpoints']['destination'], 'N7')

    def test_playback_continuous_advancement(self):
        res = bfs(self.graph, 'N1', 'N7')
        total_steps = len(res['steps'])
        self.assertGreater(total_steps, 2)
        with patch.object(sim, 'st') as mock_st:
            mock_st.session_state = {'sim_res': res, 'step_idx': 0, 'is_playing': True, 'is_paused': False}
            for step in range(total_steps - 1):
                self.assertTrue(mock_st.session_state['is_playing'])
                mock_st.session_state['step_idx'] += 1
                self.assertEqual(mock_st.session_state['step_idx'], step + 1)
            self.assertEqual(mock_st.session_state['step_idx'], total_steps - 1)
            mock_st.session_state['is_playing'] = False
            self.assertFalse(mock_st.session_state['is_playing'])

    def test_slider_does_not_reset_playing_state_during_progression(self):
        res = bfs(self.graph, 'N1', 'N7')
        total_steps = len(res['steps'])
        with patch.object(sim, 'st') as mock_st:
            mock_st.session_state = {'sim_res': res, 'step_idx': 1, 'is_playing': True, 'is_paused': False, 'sim_scrubber': 1}
            cur_slider_val = mock_st.session_state['step_idx'] + 1
            if mock_st.session_state.get('is_playing', False):
                mock_st.session_state['sim_scrubber'] = cur_slider_val
            self.assertEqual(mock_st.session_state['sim_scrubber'], 2)
            self.assertTrue(mock_st.session_state['is_playing'])
            self.assertEqual(mock_st.session_state['step_idx'], 1)
if __name__ == '__main__':
    unittest.main()
