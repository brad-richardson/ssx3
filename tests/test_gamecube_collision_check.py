import copy
import unittest

from gamecube_collision_check import assess


class CollisionAcceptanceTests(unittest.TestCase):
    def fixture(self):
        recipe = dict(track=8, output_sha256='world', collisions=dict(
            enabled_instances=[dict(source_instance=9, instance=767)]))
        receipt = dict(exit_code=0, world_archive_sha256='world', evidence=dict(
            module_loaded=True, invalid_memory_accesses=0, gpu_command_errors=0,
            unknown_guest_instructions=0, fallback_jit_runs=0,
            shutdown_counters=dict(native=100, smc_failed=0)))
        observations = dict(riding_observed_after_start=True, reset_loops=[])
        events = [dict(stage=s, instance_id=0x080002ff, contacts=c, bounds=[0, 0, 0, 10, 10, 10])
                  for s, c in [('bound', -1), ('narrow_enter', -1), ('narrow_exit', 2)]]
        return recipe, receipt, observations, events, [], 9

    def test_positive_object_contact_does_not_claim_player_or_full_course(self):
        result = assess(*self.fixture())
        self.assertTrue(result['selected_obstacle_contact_verified'])
        self.assertEqual(result['positive_returns'], 1)
        self.assertEqual(result['summed_contact_counts'], 2)
        self.assertFalse(result['player_query_identity_verified'])
        self.assertIsNone(result['first_spatially_near_player_reaction'])

    def test_clean_ride_and_registered_object_without_contact_is_not_success(self):
        args = self.fixture()
        args[3][-1]['contacts'] = 0
        self.assertFalse(assess(*args)['selected_obstacle_contact_verified'])
        args[3][:] = args[3][:1]
        report = assess(*args)
        self.assertFalse(report['narrow_phase_observed'])
        self.assertFalse(report['selected_obstacle_contact_verified'])

    def test_wrong_world_instance_and_overflow_rejected(self):
        args = self.fixture()
        bad = copy.deepcopy(args)
        bad[1]['world_archive_sha256'] = 'other-world'
        with self.assertRaisesRegex(ValueError, 'Runtime world'):
            assess(*bad)
        bad = copy.deepcopy(args)
        bad[3][-1]['instance_id'] += 1
        with self.assertRaisesRegex(ValueError, 'selected obstacle'):
            assess(*bad)
        bad = copy.deepcopy(args)
        bad[3].append(dict(stage='overflow'))
        with self.assertRaisesRegex(ValueError, 'overflow'):
            assess(*bad)

    def test_candidate_may_be_any_installed_world_archive(self):
        """A course-redirect directory boots one of several archives, not bam.big."""
        args = copy.deepcopy(self.fixture())
        args[1]['world_archive_sha256'] = 'stock-bam'
        args[1]['world_archives_sha256'] = {'bam.big': 'stock-bam', 'alo.big': 'world'}
        self.assertTrue(assess(*args)['selected_obstacle_contact_verified'])
        args[1]['world_archives_sha256'] = {'bam.big': 'stock-bam', 'alo.big': 'another'}
        with self.assertRaisesRegex(ValueError, 'Runtime world'):
            assess(*args)

    def test_absent_shutdown_fault_and_reset_loop_rejected(self):
        for alter in (lambda a: a[1]['evidence'].pop('shutdown_counters'),
                      lambda a: a[1]['evidence'].update(gpu_command_errors=1),
                      lambda a: a[2].update(reset_loops=[dict(first_reset_t=1)]),
                      lambda a: a[2].update(riding_observed_after_start=False)):
            args = self.fixture()
            alter(args)
            with self.assertRaises(ValueError):
                assess(*args)


if __name__ == '__main__':
    unittest.main()
