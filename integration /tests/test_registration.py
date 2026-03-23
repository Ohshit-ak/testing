"""
tests/test_registration.py
Unit tests for RegistrationModule.
"""

import unittest
from helpers import make_modules


class TestRegistration(unittest.TestCase):

    def setUp(self):
        self.reg, self.crew, *_ = make_modules()

    # ── Happy path ────────────────────────────────────────────────────────────

    def test_register_valid_driver(self):
        member = self.reg.register("Dom Torretto", "driver")
        self.assertEqual(member.name, "Dom Torretto")
        self.assertEqual(member.role, "driver")
        self.assertTrue(member.is_active)

    def test_register_valid_mechanic(self):
        member = self.reg.register("Tej Parker", "mechanic")
        self.assertEqual(member.role, "mechanic")

    def test_register_all_valid_roles(self):
        roles = ["driver", "mechanic", "strategist", "scout", "medic"]
        for i, role in enumerate(roles):
            m = self.reg.register(f"Member {i}", role)
            self.assertEqual(m.role, role)

    def test_register_returns_unique_ids(self):
        m1 = self.reg.register("Alice", "driver")
        m2 = self.reg.register("Bob", "mechanic")
        self.assertNotEqual(m1.member_id, m2.member_id)

    def test_get_member_returns_correct_member(self):
        member = self.reg.register("Letty", "driver")
        fetched = self.reg.get_member(member.member_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Letty")

    def test_get_member_unknown_id_returns_none(self):
        result = self.reg.get_member("00000000-0000-0000-0000-000000000000")
        self.assertIsNone(result)

    def test_get_active_members_includes_new_member(self):
        member = self.reg.register("Roman", "strategist")
        active = self.reg.get_active_members()
        ids = [m.member_id for m in active]
        self.assertIn(member.member_id, ids)

    def test_get_members_by_role_filters_correctly(self):
        driver   = self.reg.register("Alice", "driver")
        mechanic = self.reg.register("Bob",   "mechanic")
        drivers  = self.reg.get_members_by_role("driver")
        self.assertEqual(len(drivers), 1)
        self.assertEqual(drivers[0].member_id, driver.member_id)

    def test_get_members_by_role_multiple(self):
        self.reg.register("Alice", "driver")
        self.reg.register("Bob",   "driver")
        self.reg.register("Carol", "mechanic")
        drivers = self.reg.get_members_by_role("driver")
        self.assertEqual(len(drivers), 2)

    # ── Deactivation ──────────────────────────────────────────────────────────

    def test_deactivate_sets_inactive(self):
        member = self.reg.register("Suki", "scout")
        self.reg.deactivate(member.member_id)
        self.assertFalse(self.reg.get_member(member.member_id).is_active)

    def test_deactivate_removes_from_active_members(self):
        member = self.reg.register("Suki", "scout")
        self.reg.deactivate(member.member_id)
        active_ids = [m.member_id for m in self.reg.get_active_members()]
        self.assertNotIn(member.member_id, active_ids)

    def test_deactivate_removes_from_role_query(self):
        member = self.reg.register("Suki", "scout")
        self.reg.deactivate(member.member_id)
        scouts = self.reg.get_members_by_role("scout")
        self.assertEqual(len(scouts), 0)

    # ── Error cases ───────────────────────────────────────────────────────────

    def test_register_duplicate_name_raises(self):
        self.reg.register("Dom Torretto", "driver")
        with self.assertRaises(ValueError):
            self.reg.register("Dom Torretto", "mechanic")

    def test_register_duplicate_name_case_insensitive(self):
        self.reg.register("Dom Torretto", "driver")
        with self.assertRaises(ValueError):
            self.reg.register("dom torretto", "driver")

    def test_register_invalid_role_raises(self):
        with self.assertRaises(ValueError):
            self.reg.register("Ghost Rider", "hacker")

    def test_register_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.reg.register("", "driver")

    def test_register_whitespace_only_name_raises(self):
        with self.assertRaises(ValueError):
            self.reg.register("   ", "driver")

    def test_deactivate_unknown_id_raises(self):
        with self.assertRaises(KeyError):
            self.reg.deactivate("00000000-0000-0000-0000-000000000000")


if __name__ == "__main__":
    unittest.main()
