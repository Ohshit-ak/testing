"""
tests/test_crew_management.py
Unit tests for CrewManagementModule.
"""

import unittest
import uuid
from helpers import make_modules, register_driver, register_mechanic


class TestCrewManagement(unittest.TestCase):

    def setUp(self):
        self.reg, self.crew, *_ = make_modules()

    # ── Profile creation ──────────────────────────────────────────────────────

    def test_add_profile_valid(self):
        member = self.reg.register("Alice", "driver")
        profile = self.crew.add_profile(member.member_id, skill_level=8)
        self.assertEqual(profile.skill_level, 8)
        self.assertEqual(profile.member_id, member.member_id)

    def test_add_profile_default_skill_is_five(self):
        member = self.reg.register("Bob", "mechanic")
        profile = self.crew.add_profile(member.member_id)
        self.assertEqual(profile.skill_level, 5)

    def test_add_profile_stores_in_get_profile(self):
        member = self.reg.register("Carol", "strategist")
        self.crew.add_profile(member.member_id, skill_level=6)
        profile = self.crew.get_profile(member.member_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.skill_level, 6)

    # ── Skill updates ─────────────────────────────────────────────────────────

    def test_update_skill_valid(self):
        member = register_driver(self.reg, self.crew)
        self.crew.update_skill(member.member_id, 10)
        self.assertEqual(self.crew.get_profile(member.member_id).skill_level, 10)

    def test_update_skill_boundary_min(self):
        member = register_driver(self.reg, self.crew)
        self.crew.update_skill(member.member_id, 1)
        self.assertEqual(self.crew.get_profile(member.member_id).skill_level, 1)

    def test_update_skill_boundary_max(self):
        member = register_driver(self.reg, self.crew)
        self.crew.update_skill(member.member_id, 10)
        self.assertEqual(self.crew.get_profile(member.member_id).skill_level, 10)

    # ── Specialisations ───────────────────────────────────────────────────────

    def test_add_specialisation_stored(self):
        member = register_driver(self.reg, self.crew)
        self.crew.add_specialisation(member.member_id, "Drag Racing")
        profile = self.crew.get_profile(member.member_id)
        self.assertIn("drag racing", profile.specialisations)

    def test_add_specialisation_no_duplicates(self):
        member = register_driver(self.reg, self.crew)
        self.crew.add_specialisation(member.member_id, "drift")
        self.crew.add_specialisation(member.member_id, "drift")
        self.assertEqual(profile := self.crew.get_profile(member.member_id),
                         profile)  # just get profile
        self.assertEqual(len(self.crew.get_profile(member.member_id).specialisations), 1)

    # ── Availability ──────────────────────────────────────────────────────────

    def test_availability_default_true(self):
        member = register_driver(self.reg, self.crew)
        self.assertTrue(self.crew.is_available(member.member_id))

    def test_set_availability_false(self):
        member = register_driver(self.reg, self.crew)
        self.crew.set_availability(member.member_id, False)
        self.assertFalse(self.crew.is_available(member.member_id))

    def test_set_availability_restore_true(self):
        member = register_driver(self.reg, self.crew)
        self.crew.set_availability(member.member_id, False)
        self.crew.set_availability(member.member_id, True)
        self.assertTrue(self.crew.is_available(member.member_id))

    def test_is_available_no_profile_returns_false(self):
        member = self.reg.register("Ghost", "driver")   # registered but no profile
        self.assertFalse(self.crew.is_available(member.member_id))

    def test_get_available_by_role_filters_busy(self):
        d1 = register_driver(self.reg, self.crew, name="Free Driver")
        d2 = register_driver(self.reg, self.crew, name="Busy Driver")
        self.crew.set_availability(d2.member_id, False)
        available = self.crew.get_available_by_role("driver")
        ids = [m.member_id for m in available]
        self.assertIn(d1.member_id, ids)
        self.assertNotIn(d2.member_id, ids)

    def test_get_available_by_role_empty_when_all_busy(self):
        d = register_driver(self.reg, self.crew)
        self.crew.set_availability(d.member_id, False)
        self.assertEqual(self.crew.get_available_by_role("driver"), [])

    # ── Stat recording ────────────────────────────────────────────────────────

    def test_record_race_increments_count(self):
        member = register_driver(self.reg, self.crew)
        self.crew.record_race(member.member_id)
        self.crew.record_race(member.member_id)
        self.assertEqual(self.crew.get_profile(member.member_id).race_count, 2)

    def test_record_mission_increments_count(self):
        member = register_driver(self.reg, self.crew)
        self.crew.record_mission(member.member_id)
        self.assertEqual(self.crew.get_profile(member.member_id).mission_count, 1)

    # ── Error cases ───────────────────────────────────────────────────────────

    def test_add_profile_unregistered_raises(self):
        with self.assertRaises(ValueError):
            self.crew.add_profile(str(uuid.uuid4()), skill_level=5)

    def test_add_profile_duplicate_raises(self):
        member = register_driver(self.reg, self.crew)
        with self.assertRaises(ValueError):
            self.crew.add_profile(member.member_id, skill_level=5)

    def test_update_skill_above_max_raises(self):
        member = register_driver(self.reg, self.crew)
        with self.assertRaises(ValueError):
            self.crew.update_skill(member.member_id, 11)

    def test_update_skill_below_min_raises(self):
        member = register_driver(self.reg, self.crew)
        with self.assertRaises(ValueError):
            self.crew.update_skill(member.member_id, 0)

    def test_add_profile_skill_above_max_raises(self):
        member = self.reg.register("Over", "driver")
        with self.assertRaises(ValueError):
            self.crew.add_profile(member.member_id, skill_level=11)

    def test_add_profile_inactive_member_raises(self):
        member = self.reg.register("Inactive", "driver")
        self.reg.deactivate(member.member_id)
        with self.assertRaises(ValueError):
            self.crew.add_profile(member.member_id)


if __name__ == "__main__":
    unittest.main()
