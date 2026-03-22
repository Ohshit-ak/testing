"""
tests/test_results.py
Unit tests for ResultsModule.
"""

import unittest
from tests.helpers import (
    make_modules, register_driver, add_good_car, run_full_race
)
from results import DAMAGE_PER_RACE, PRIZE_SPLIT


class TestResults(unittest.TestCase):

    def setUp(self):
        (self.reg, self.crew, self.inv,
         self.race_mgmt, self.results, *_) = make_modules(starting_cash=20_000.0)

    def _setup_race(self, prize_pool=10_000.0, names=("Driver A", "Driver B")):
        """Helper: register two drivers, enter them, start race. Returns (race, d1, d2, c1, c2)."""
        d1 = register_driver(self.reg, self.crew, name=names[0])
        d2 = register_driver(self.reg, self.crew, name=names[1])
        c1 = add_good_car(self.inv, make="Ford",  model="Mustang")
        c2 = add_good_car(self.inv, make="Chevy", model="Camaro")
        r  = self.race_mgmt.create_race("Test Race", "LA", prize_pool)
        self.race_mgmt.enter_race(r.race_id, d1.member_id, c1.car_id)
        self.race_mgmt.enter_race(r.race_id, d2.member_id, c2.car_id)
        self.race_mgmt.start_race(r.race_id)
        return r, d1, d2, c1, c2

    # ── Happy path ────────────────────────────────────────────────────────────

    def test_record_result_sets_finished(self):
        r, d1, d2, *_ = self._setup_race()
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        self.assertEqual(r.status, "FINISHED")

    def test_first_place_prize_credited(self):
        prize_pool = 10_000.0
        r, d1, d2, *_ = self._setup_race(prize_pool=prize_pool)
        balance_before = self.inv.cash_balance
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        expected_total_prize = prize_pool * (PRIZE_SPLIT[1] + PRIZE_SPLIT[2])
        self.assertAlmostEqual(
            self.inv.cash_balance,
            balance_before + expected_total_prize,
            places=2
        )

    def test_first_place_gets_50_percent(self):
        prize_pool = 10_000.0
        r, d1, d2, *_ = self._setup_race(prize_pool=prize_pool)
        result = self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        self.assertAlmostEqual(
            result.prizes_awarded[d1.member_id],
            prize_pool * 0.50,
            places=2
        )

    def test_second_place_gets_30_percent(self):
        prize_pool = 10_000.0
        r, d1, d2, *_ = self._setup_race(prize_pool=prize_pool)
        result = self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        self.assertAlmostEqual(
            result.prizes_awarded[d2.member_id],
            prize_pool * 0.30,
            places=2
        )

    def test_cars_damaged_after_race(self):
        r, d1, d2, c1, c2 = self._setup_race()
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        self.assertLess(self.inv.get_car(c1.car_id).condition, 100)
        self.assertLess(self.inv.get_car(c2.car_id).condition, 100)

    def test_car_condition_reduced_by_damage_constant(self):
        r, d1, d2, c1, c2 = self._setup_race()
        cond_before = self.inv.get_car(c1.car_id).condition
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        self.assertEqual(
            self.inv.get_car(c1.car_id).condition,
            cond_before - DAMAGE_PER_RACE
        )

    def test_drivers_freed_after_result(self):
        r, d1, d2, *_ = self._setup_race()
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        self.assertTrue(self.crew.is_available(d1.member_id))
        self.assertTrue(self.crew.is_available(d2.member_id))

    def test_cars_released_after_result(self):
        r, d1, d2, c1, c2 = self._setup_race()
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        self.assertFalse(self.inv.get_car(c1.car_id).is_in_use)
        self.assertFalse(self.inv.get_car(c2.car_id).is_in_use)

    def test_winner_ranking_updated(self):
        r, d1, d2, *_ = self._setup_race()
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        ranking = self.results._rankings[d1.member_id]
        self.assertEqual(ranking.wins, 1)
        self.assertEqual(ranking.total_races, 1)

    def test_second_place_has_zero_wins(self):
        r, d1, d2, *_ = self._setup_race()
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        ranking = self.results._rankings[d2.member_id]
        self.assertEqual(ranking.wins, 0)
        self.assertEqual(ranking.podiums, 1)

    def test_race_count_incremented_for_both_drivers(self):
        r, d1, d2, *_ = self._setup_race()
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        self.assertEqual(self.crew.get_profile(d1.member_id).race_count, 1)
        self.assertEqual(self.crew.get_profile(d2.member_id).race_count, 1)

    def test_result_object_stored(self):
        r, d1, d2, *_ = self._setup_race()
        result = self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        self.assertIsNotNone(result.result_id)
        self.assertEqual(result.race_name, "Test Race")

    # ── Error cases ───────────────────────────────────────────────────────────

    def test_record_result_on_open_race_raises(self):
        d1 = register_driver(self.reg, self.crew, name="D1")
        d2 = register_driver(self.reg, self.crew, name="D2")
        c1 = add_good_car(self.inv)
        c2 = add_good_car(self.inv)
        r  = self.race_mgmt.create_race("Open", "LA", 1000.0)
        self.race_mgmt.enter_race(r.race_id, d1.member_id, c1.car_id)
        self.race_mgmt.enter_race(r.race_id, d2.member_id, c2.car_id)
        # NOT started — status is OPEN
        with self.assertRaises(ValueError):
            self.results.record_result(r.race_id, [d1.member_id, d2.member_id])

    def test_record_result_mismatched_order_raises(self):
        r, d1, d2, *_ = self._setup_race()
        with self.assertRaises(ValueError):
            self.results.record_result(r.race_id, [d1.member_id])  # missing d2

    def test_no_double_result_on_finished_race(self):
        r, d1, d2, *_ = self._setup_race()
        self.results.record_result(r.race_id, [d1.member_id, d2.member_id])
        with self.assertRaises(ValueError):
            self.results.record_result(r.race_id, [d1.member_id, d2.member_id])

    def test_record_result_unknown_race_raises(self):
        with self.assertRaises(KeyError):
            self.results.record_result("no-such-race", [])


if __name__ == "__main__":
    unittest.main()
