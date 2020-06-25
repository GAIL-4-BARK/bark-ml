import os
import pickle
import unittest
import numpy as np
import shutil
from bark_ml.library_wrappers.lib_tf2rl.generate_expert_trajectories \
    import *

# Please add a new test case class for every function you test.
# Modularise the tests as much as possible, but on a reasonable scale.

interaction_data_set_mock_path = os.path.join(
    os.path.dirname(__file__), 'data/interaction_data_set_mock')
known_key = ('DR_DEU_Merging_MT/DR_DEU_Merging_MT_v01_shifted',
             'DR_DEU_Merging_MT/vehicle_tracks_013')


class CalculateActionTests(unittest.TestCase):
    """
    Tests for the calculate action function.
    """

    def test_calculate_action(self):
        """
        Test: Calculate the action based on two consecutive observations.
        """
        # TODO Add more working examples as just this single
        observations = [[0] * 12, [1000] * 12]
        timestamps = [1000, 2000]

        expected_action = [1.2160906747839564, 1.0]

        self.assertEqual(
            expected_action,
            calculate_action(observations[1], observations[0], timestamps[1], timestamps[0], 2.7))

    def test_calculate_action_timestamps_are_equal(self):
        """
        Test: Calculate the action based on two consecutive observations.
        """
        observations = [[0] * 12, [1000] * 12]
        timestamps = [1000, 1000]

        expected_action = [0.0, 0.0]

        self.assertEqual(
            expected_action,
            calculate_action(observations[1], observations[0], timestamps[1], timestamps[0], 2.7))


class GetMapAndTrackFilesTests(unittest.TestCase):
    """
    Tests: get_track_files and get_map_files
    """

    def test_get_track_files(self):
        """
        Test: get_track_files
        """
        track_files = get_track_files(interaction_data_set_mock_path)

        self.assertIs(len(track_files), 1)
        self.assertIs(track_files[0].endswith(
            'bark_ml/tests/py_library_tf2rl_tests/data/interaction_data_set_mock/DR_DEU_Merging_MT/tracks/vehicle_tracks_013.csv'), True)

    def test_load_map_files(self):
        """
        Test: get_map_files
        """
        map_files = get_map_files(interaction_data_set_mock_path)

        self.assertIs(len(map_files), 1)
        self.assertIs(map_files[0].endswith(
            'bark_ml/tests/py_library_tf2rl_tests/data/interaction_data_set_mock/DR_DEU_Merging_MT/map/DR_DEU_Merging_MT_v01_shifted.xodr'), True)

    def test_interaction_data_set_path_invalid(self):
        """
        Test: The given path is not an interaction dataset path
        """
        with self.assertRaises(ValueError):
            map_files = get_map_files(os.path.dirname(__file__))


class CreateParameterServersForScenariosTests(unittest.TestCase):
    """
    Tests: create_parameter_servers_for_scenarios
    """

    def test_create_parameter_servers_for_scenarios(self):
        """
        Test: Valid parameter server
        """

        param_servers = create_parameter_servers_for_scenarios(
            interaction_data_set_mock_path)
        self.assertIn(known_key, param_servers)

        param_server = param_servers[known_key]
        assert param_server["Scenario"]["Generation"]["InteractionDatasetScenarioGeneration"]["MapFilename"].endswith(
            'bark_ml/tests/py_library_tf2rl_tests/data/interaction_data_set_mock/DR_DEU_Merging_MT/map/DR_DEU_Merging_MT_v01_shifted.xodr')
        assert param_server["Scenario"]["Generation"]["InteractionDatasetScenarioGeneration"]["TrackFilename"].endswith(
            'bark_ml/tests/py_library_tf2rl_tests/data/interaction_data_set_mock/DR_DEU_Merging_MT/tracks/vehicle_tracks_013.csv')

        track_ids = [i for i in range(1, 87) if i != 18]
        self.assertEqual(param_server["Scenario"]["Generation"]
                         ["InteractionDatasetScenarioGeneration"]["TrackIds"], track_ids)

        self.assertEqual(param_server["Scenario"]["Generation"]
                         ["InteractionDatasetScenarioGeneration"]["StartTs"], 100)
        self.assertEqual(param_server["Scenario"]["Generation"]
                         ["InteractionDatasetScenarioGeneration"]["EndTs"], 327300)

        param_server["Scenario"]["Generation"]["InteractionDatasetScenarioGeneration"]["EgoTrackId"] = 1


class CreateScenarioTests(unittest.TestCase):
    """
    Tests: create_scenario
    """

    def test_create_scenario(self):
        """
        Test: Valid scenario
        """
        param_servers = create_parameter_servers_for_scenarios(
            interaction_data_set_mock_path)
        self.assertIn(known_key, param_servers)

        scenario, start_ts, end_ts = create_scenario(param_servers[known_key])
        self.assertEqual(start_ts, 100)
        self.assertEqual(end_ts, 327300)

        assert scenario.map_file_name.endswith(
            'bark_ml/tests/py_library_tf2rl_tests/data/interaction_data_set_mock/DR_DEU_Merging_MT/map/DR_DEU_Merging_MT_v01_shifted.xodr')
        self.assertEqual(len(scenario._agent_list), 86)


class SimulationBasedTests(unittest.TestCase):
    """
    Base class for simulation based tests
    """

    def setUp(self):
        """
        Setup
        """
        param_servers = create_parameter_servers_for_scenarios(
            interaction_data_set_mock_path)
        self.assertIn(known_key, param_servers)

        param_server = param_servers[known_key]
        param_server["Scenario"]["Generation"]["InteractionDatasetScenarioGeneration"]["TrackIds"] = [
            63, 64, 65, 66, 67, 68]
        param_server["Scenario"]["Generation"]["InteractionDatasetScenarioGeneration"]["StartTs"] = 232000
        param_server["Scenario"]["Generation"]["InteractionDatasetScenarioGeneration"]["EndTs"] = 259000
        self.test_agent_id = 65
        param_server["Scenario"]["Generation"]["InteractionDatasetScenarioGeneration"]["EgoTrackId"] = self.test_agent_id
        self.param_server = param_server
        self.expert_trajectories = {}
        self.sim_time_step = 100


class SimulateScenarioTests(SimulationBasedTests):
    """
    Tests: simulate_scenario
    """

    def test_simulate_scenario_no_renderer(self):
        """
        Test: Replay scenario with no renderer
        """
        self.expert_trajectories = simulate_scenario(
            self.param_server, sim_time_step=self.sim_time_step)

    @unittest.skip("Does not work when using bazel test :unit_tests" + " Comment out this line to run it, but comment it again before pushing and running the :unit_tests")
    def test_simulate_scenario_pygame(self):
        """
        Test: Replay scenario with pygame renderer
        """
        self.expert_trajectories = simulate_scenario(
            self.param_server, sim_time_step=self.sim_time_step, renderer="pygame")

    @unittest.skip("Does not work when using bazel test :unit_tests" + " Comment out this line to run it, but comment it again before pushing and running the :unit_tests")
    def test_simulate_scenario_matplotlib(self):
        """
        Test: Replay scenario with matplotlib renderer
        """
        self.expert_trajectories = simulate_scenario(
            self.param_server, sim_time_step=self.sim_time_step, renderer="matplotlib")

    def tearDown(self):
        """
        Tear down
        """
        for agent_id in range(63, 69):
            self.assertIn(agent_id, self.expert_trajectories)
            agent_expert_trajectories = self.expert_trajectories[agent_id]
            for key in ['obs', 'time', 'merge', 'wheelbase']:
                self.assertIn(key, agent_expert_trajectories)
                assert len(agent_expert_trajectories[key]) == 269

            for wheelbase in agent_expert_trajectories['wheelbase']:
                assert wheelbase == 2.7

            times = agent_expert_trajectories['time']
            for i in range(1, len(times)):
                self.assertAlmostEqual(times[i] - times[i - 1], self.sim_time_step / 1000, delta=1e-5)


class MeasureWorldTests(SimulationBasedTests):
    """
    Tests: measure_world
    """

    def setUp(self):
        """
        Setup
        """
        super().setUp()
        scenario, start_ts, end_ts = create_scenario(self.param_server)
        self.sim_time_step = 100
        self.sim_steps = int((end_ts - start_ts)/(self.sim_time_step))
        self.sim_time_step_seconds = self.sim_time_step / 1000

        self.observer = NearestAgentsObserver(self.param_server)
        self.world_state = scenario.GetWorldState()

    def test_measure_world(self):
        """
        Test: measure_world
        """
        current_measurement = np.array([0.0] * 12)
        previous_measurement = np.zeros_like(current_measurement)
        max_values = np.zeros_like(previous_measurement)
        min_values = np.zeros_like(previous_measurement)

        for _ in range(0, self.sim_steps):
            self.world_state.Step(self.sim_time_step_seconds)

            previous_measurement = current_measurement
            all_measurements = measure_world(self.world_state, self.observer)

            if self.test_agent_id in all_measurements:
                current_measurement = all_measurements[self.test_agent_id]['obs']

                difference = current_measurement - previous_measurement

                for i in range(difference.shape[0]):
                    if max_values[i] < difference[i]:
                        max_values[i] = difference[i]
                    if min_values[i] > difference[i]:
                        min_values[i] = difference[i]

        expected_max_values = np.array([0.54980648, 0.55021292, 0.48717329, 0.01684499, 0.5499202,
                                        0.55034626, 0.49115214, 0.02198388, 0.54953927, 0.5503884, 0.4895606, 0.02255795])
        expected_min_values = np.array([-1.77621841e-05, -8.94069672e-07, -7.95662403e-04, -7.10122287e-04, -1.01149082e-03,
                                        -2.86102295e-05, -2.70859301e-02, -8.40493664e-03, -9.69946384e-04, -3.43322754e-05, -2.70856917e-02, -4.82387096e-03])

        for i in range(expected_max_values.shape[0]):
            self.assertAlmostEqual(expected_max_values[i], max_values[i])
            self.assertAlmostEqual(expected_min_values[i], min_values[i])


class GenerateExpertTrajectoriesForScenarioTests(SimulationBasedTests):
    """
    Tests: generate_expert_trajectories_for_scenario
    """

    def test_generate_expert_trajectories_for_scenario(self):
        """
        Test: generate_expert_trajectories_for_scenario
        """
        self.setUp()
        self.expert_trajectories = generate_expert_trajectories_for_scenario(self.param_server, self.sim_time_step)

        for agent_id in self.expert_trajectories:
            actions = self.expert_trajectories[agent_id]['act']
            assert len(actions) == len(self.expert_trajectories[agent_id]['obs'])
            assert len(actions[0]) == 2

            dones = self.expert_trajectories[agent_id]['done']
            for i in range(len(dones) - 1):
                dones[i] == 0
            
            dones[-1] = 1


class StoreExpertTrajectoriesTests(unittest.TestCase):
    """
    Tests: store_expert_trajectories
    """

    def test_store_expert_trajectories(self):
        """
        Test: store_expert_trajectories
        """
        map = "test_map_name"
        track = "test/test_track_name"
        expert_trajectories_path = os.path.join(os.path.dirname(__file__), 'test_store_expert_trajectories')
        expert_trajectories = {'foo': 'bar'}
        store_expert_trajectories(map, track, expert_trajectories_path, expert_trajectories)

        file_name = os.path.join(expert_trajectories_path, 'test_map_name', 'test_track_name.pkl')
        with open(file_name, 'rb') as pickle_file:
            loaded_expert_trajectories = dict(pickle.load(pickle_file))
            self.assertDictEqual(loaded_expert_trajectories, expert_trajectories)
        shutil.rmtree(expert_trajectories_path)


if __name__ == '__main__':
    unittest.main()