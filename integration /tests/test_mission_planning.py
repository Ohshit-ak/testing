"""
tests/test_mission_planning.py
Unit tests for MissionPlanningModule.
"""

import unittest
from helpers import (
    make_modules, register_driver, register_mechanic,
    register_medic, register_scout, register_strategist
)


class TestMissionPlanning(unittest.TestCase):

    def setUp(self):
        (self.reg, self.crew, self.inv,
         _, _, self.miss, *_) = make_modules(starting_cash=10_000.0)

    # ── Mission planning ─────────────────────────────────────────────────────

    def test_plan_delivery_with_driver_available(self):
        register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Drop package at Sunset")
        self.assertEqual(m.status, "PENDING")
        self.assertEqual(m.mission_type, "delivery")

    def test_plan_mission_sets_default_cost_and_reward(self):
        register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.assertGreater(m.cost, 0)
        self.assertGreater(m.reward, 0)

    def test_plan_mission_custom_cost_and_reward(self):
        register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Custom", custom_cost=99.0, custom_reward=999.0)
        self.assertAlmostEqual(m.cost,   99.0,  places=2)
        self.assertAlmostEqual(m.reward, 999.0, places=2)

    def test_plan_rescue_requires_driver_and_medic(self):
        register_driver(self.reg, self.crew)
        register_medic(self.reg, self.crew)
        m = self.miss.plan_mission("rescue", "Extract racer")
        self.assertIsNotNone(m)

    def test_plan_recon_requires_scout(self):
        register_scout(self.reg, self.crew)
        m = self.miss.plan_mission("recon", "Survey location")
        self.assertIsNotNone(m)

    # ── Member assignment ─────────────────────────────────────────────────────

    def test_assign_driver_to_delivery(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.assertIn(d.member_id, m.assigned_members)

    def test_assign_marks_member_unavailable(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.assertFalse(self.crew.is_available(d.member_id))

    # ── Mission lifecycle ─────────────────────────────────────────────────────

    def test_start_mission_sets_in_progress(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.miss.start_mission(m.mission_id)
        self.assertEqual(m.status, "IN_PROGRESS")

    def test_start_mission_debits_cost(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        balance_before = self.inv.cash_balance
        self.miss.start_mission(m.mission_id)
        self.assertAlmostEqual(
            self.inv.cash_balance, balance_before - m.cost, places=2
        )

    def test_complete_mission_success_credits_reward(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.miss.start_mission(m.mission_id)
        balance_before = self.inv.cash_balance
        self.miss.complete_mission(m.mission_id, success=True)
        self.assertAlmostEqual(
            self.inv.cash_balance, balance_before + m.reward, places=2
        )

    def test_complete_mission_failure_no_reward(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.miss.start_mission(m.mission_id)
        balance_before = self.inv.cash_balance
        self.miss.complete_mission(m.mission_id, success=False)
        self.assertAlmostEqual(self.inv.cash_balance, balance_before, places=2)

    def test_complete_mission_sets_completed(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.miss.start_mission(m.mission_id)
        self.miss.complete_mission(m.mission_id, success=True)
        self.assertEqual(m.status, "COMPLETED")

    def test_complete_mission_failure_sets_failed(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.miss.start_mission(m.mission_id)
        self.miss.complete_mission(m.mission_id, success=False)
        self.assertEqual(m.status, "FAILED")

    def test_complete_mission_frees_members(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.miss.start_mission(m.mission_id)
        self.miss.complete_mission(m.mission_id, success=True)
        self.assertTrue(self.crew.is_available(d.member_id))

    def test_complete_mission_increments_mission_count(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.miss.start_mission(m.mission_id)
        self.miss.complete_mission(m.mission_id, success=True)
        self.assertEqual(self.crew.get_profile(d.member_id).mission_count, 1)

    def test_abort_pending_mission_frees_member(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.miss.abort_mission(m.mission_id)
        self.assertTrue(self.crew.is_available(d.member_id))

    # ── Error cases ───────────────────────────────────────────────────────────

    def test_plan_mission_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            self.miss.plan_mission("assassination", "Shady job")

    def test_plan_mission_no_available_driver_raises(self):
        # No drivers registered at all
        with self.assertRaises(ValueError):
            self.miss.plan_mission("delivery", "No one to deliver")

    def test_plan_rescue_no_medic_raises(self):
        register_driver(self.reg, self.crew)  # driver present, but no medic
        with self.assertRaises(ValueError):
            self.miss.plan_mission("rescue", "Need a medic")

    def test_assign_wrong_role_raises(self):
        mech = register_mechanic(self.reg, self.crew)
        register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Drivers only")
        with self.assertRaises(ValueError):
            self.miss.assign_member(m.mission_id, mech.member_id)

    def test_assign_unavailable_member_raises(self):
        d = register_driver(self.reg, self.crew)
        self.crew.set_availability(d.member_id, False)
        # Need a second driver to plan the mission
        register_driver(self.reg, self.crew, name="Backup Driver")
        m = self.miss.plan_mission("delivery", "Test")
        with self.assertRaises(ValueError):
            self.miss.assign_member(m.mission_id, d.member_id)

    def test_start_mission_missing_role_raises(self):
        register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        # Don't assign anyone
        with self.assertRaises(ValueError):
            self.miss.start_mission(m.mission_id)

    def test_complete_not_in_progress_raises(self):
        register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        with self.assertRaises(ValueError):
            self.miss.complete_mission(m.mission_id, success=True)

    def test_abort_in_progress_mission_raises(self):
        d = register_driver(self.reg, self.crew)
        m = self.miss.plan_mission("delivery", "Test")
        self.miss.assign_member(m.mission_id, d.member_id)
        self.miss.start_mission(m.mission_id)
        with self.assertRaises(ValueError):
            self.miss.abort_mission(m.mission_id)


if __name__ == "__main__":
    unittest.main()
