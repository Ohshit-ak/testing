"""
tests/test_race_management.py
Unit tests for RaceManagementModule.
"""

import unittest
from helpers import (
    make_modules, register_driver, register_mechanic, add_good_car
)


class TestRaceManagement(unittest.TestCase):

    def setUp(self):
        self.reg, self.crew, self.inv, self.race, *_ = make_modules()

    # ── Race creation ─────────────────────────────────────────────────────────

    def test_create_race_valid(self):
        r = self.race.create_race("Midnight Mile", "East LA", 10_000.0)
        self.assertEqual(r.name, "Midnight Mile")
        self.assertEqual(r.location, "East LA")
        self.assertAlmostEqual(r.prize_pool, 10_000.0, places=2)
        self.assertEqual(r.status, "OPEN")

    def test_create_race_zero_prize_allowed(self):
        r = self.race.create_race("Free Race", "Docks", 0.0)
        self.assertAlmostEqual(r.prize_pool, 0.0, places=2)

    def test_create_race_stored_and_retrievable(self):
        r = self.race.create_race("Test Race", "Somewhere", 5000.0)
        fetched = self.race.get_race(r.race_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.race_id, r.race_id)

    def test_get_race_unknown_id_returns_none(self):
        self.assertIsNone(self.race.get_race("no-such-id"))

    # ── Race entry ────────────────────────────────────────────────────────────

    def test_enter_race_valid_driver(self):
        d = register_driver(self.reg, self.crew)
        c = add_good_car(self.inv)
        r = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d.member_id, c.car_id)
        self.assertEqual(len(r.entries), 1)

    def test_enter_race_marks_driver_unavailable(self):
        d = register_driver(self.reg, self.crew)
        c = add_good_car(self.inv)
        r = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d.member_id, c.car_id)
        self.assertFalse(self.crew.is_available(d.member_id))

    def test_enter_race_marks_car_in_use(self):
        d = register_driver(self.reg, self.crew)
        c = add_good_car(self.inv)
        r = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d.member_id, c.car_id)
        self.assertTrue(self.inv.get_car(c.car_id).is_in_use)

    def test_enter_race_get_active_entries(self):
        d = register_driver(self.reg, self.crew)
        c = add_good_car(self.inv)
        r = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d.member_id, c.car_id)
        entries = self.race.get_active_entries(r.race_id)
        self.assertEqual(entries[0], (d.member_id, c.car_id))

    # ── Race start ────────────────────────────────────────────────────────────

    def test_start_race_sets_in_progress(self):
        d1 = register_driver(self.reg, self.crew, name="D1")
        d2 = register_driver(self.reg, self.crew, name="D2")
        c1 = add_good_car(self.inv)
        c2 = add_good_car(self.inv)
        r  = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d1.member_id, c1.car_id)
        self.race.enter_race(r.race_id, d2.member_id, c2.car_id)
        self.race.start_race(r.race_id)
        self.assertEqual(r.status, "IN_PROGRESS")

    # ── Cancel race ───────────────────────────────────────────────────────────

    def test_cancel_race_sets_cancelled(self):
        r = self.race.create_race("Race", "LA", 1000.0)
        self.race.cancel_race(r.race_id)
        self.assertEqual(r.status, "CANCELLED")

    def test_cancel_race_frees_driver_and_car(self):
        d = register_driver(self.reg, self.crew)
        c = add_good_car(self.inv)
        r = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d.member_id, c.car_id)
        self.race.cancel_race(r.race_id)
        self.assertTrue(self.crew.is_available(d.member_id))
        self.assertFalse(self.inv.get_car(c.car_id).is_in_use)

    # ── Error cases ───────────────────────────────────────────────────────────

    def test_create_race_negative_prize_raises(self):
        with self.assertRaises(ValueError):
            self.race.create_race("Bad Race", "Nowhere", -500.0)

    def test_enter_race_non_driver_raises(self):
        m = register_mechanic(self.reg, self.crew)
        c = add_good_car(self.inv)
        r = self.race.create_race("Race", "LA", 1000.0)
        with self.assertRaises(ValueError):
            self.race.enter_race(r.race_id, m.member_id, c.car_id)

    def test_enter_race_low_condition_car_raises(self):
        d = register_driver(self.reg, self.crew)
        c = add_good_car(self.inv, condition=20)
        r = self.race.create_race("Race", "LA", 1000.0)
        with self.assertRaises(ValueError):
            self.race.enter_race(r.race_id, d.member_id, c.car_id)

    def test_enter_race_car_in_use_raises(self):
        d = register_driver(self.reg, self.crew)
        c = add_good_car(self.inv)
        self.inv.set_car_in_use(c.car_id, True)
        r = self.race.create_race("Race", "LA", 1000.0)
        with self.assertRaises(ValueError):
            self.race.enter_race(r.race_id, d.member_id, c.car_id)

    def test_enter_race_duplicate_driver_raises(self):
        d  = register_driver(self.reg, self.crew)
        c1 = add_good_car(self.inv)
        c2 = add_good_car(self.inv)
        r  = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d.member_id, c1.car_id)
        with self.assertRaises(ValueError):
            self.race.enter_race(r.race_id, d.member_id, c2.car_id)

    def test_enter_race_duplicate_car_raises(self):
        d1 = register_driver(self.reg, self.crew, name="D1")
        d2 = register_driver(self.reg, self.crew, name="D2")
        c  = add_good_car(self.inv)
        r  = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d1.member_id, c.car_id)
        with self.assertRaises(ValueError):
            self.race.enter_race(r.race_id, d2.member_id, c.car_id)

    def test_enter_race_unavailable_driver_raises(self):
        d = register_driver(self.reg, self.crew)
        self.crew.set_availability(d.member_id, False)
        c = add_good_car(self.inv)
        r = self.race.create_race("Race", "LA", 1000.0)
        with self.assertRaises(ValueError):
            self.race.enter_race(r.race_id, d.member_id, c.car_id)

    def test_start_race_requires_two_entries(self):
        d = register_driver(self.reg, self.crew)
        c = add_good_car(self.inv)
        r = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d.member_id, c.car_id)
        with self.assertRaises(ValueError):
            self.race.start_race(r.race_id)

    def test_enter_closed_race_raises(self):
        d1 = register_driver(self.reg, self.crew, name="D1")
        d2 = register_driver(self.reg, self.crew, name="D2")
        d3 = register_driver(self.reg, self.crew, name="D3")
        c1 = add_good_car(self.inv)
        c2 = add_good_car(self.inv)
        c3 = add_good_car(self.inv)
        r  = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d1.member_id, c1.car_id)
        self.race.enter_race(r.race_id, d2.member_id, c2.car_id)
        self.race.start_race(r.race_id)
        with self.assertRaises(ValueError):
            self.race.enter_race(r.race_id, d3.member_id, c3.car_id)

    def test_cancel_finished_race_raises(self):
        # A finished race cannot be cancelled — must go through results
        d1 = register_driver(self.reg, self.crew, name="D1")
        d2 = register_driver(self.reg, self.crew, name="D2")
        c1 = add_good_car(self.inv)
        c2 = add_good_car(self.inv)
        r  = self.race.create_race("Race", "LA", 1000.0)
        self.race.enter_race(r.race_id, d1.member_id, c1.car_id)
        self.race.enter_race(r.race_id, d2.member_id, c2.car_id)
        self.race.start_race(r.race_id)
        r.status = "FINISHED"  # simulate finished state
        with self.assertRaises(ValueError):
            self.race.cancel_race(r.race_id)


if __name__ == "__main__":
    unittest.main()
