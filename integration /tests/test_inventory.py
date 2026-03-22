"""
tests/test_inventory.py
Unit tests for InventoryModule.
"""

import unittest
from tests.helpers import make_modules, add_good_car


class TestInventory(unittest.TestCase):

    def setUp(self):
        _, _, self.inv, *_ = make_modules(starting_cash=10_000.0)

    # ── Cash operations ───────────────────────────────────────────────────────

    def test_initial_cash_balance(self):
        self.assertAlmostEqual(self.inv.cash_balance, 10_000.0, places=2)

    def test_credit_increases_balance(self):
        self.inv.credit(500.0, "test")
        self.assertAlmostEqual(self.inv.cash_balance, 10_500.0, places=2)

    def test_credit_exact_amount(self):
        before = self.inv.cash_balance
        self.inv.credit(1234.56, "precise")
        self.assertAlmostEqual(self.inv.cash_balance, before + 1234.56, places=2)

    def test_debit_decreases_balance(self):
        self.inv.debit(200.0, "test")
        self.assertAlmostEqual(self.inv.cash_balance, 9_800.0, places=2)

    def test_multiple_credits_and_debits(self):
        self.inv.credit(1000.0)
        self.inv.debit(300.0)
        self.inv.credit(50.0)
        self.assertAlmostEqual(self.inv.cash_balance, 10_750.0, places=2)

    def test_debit_entire_balance(self):
        self.inv.debit(10_000.0)
        self.assertAlmostEqual(self.inv.cash_balance, 0.0, places=2)

    # ── Cars ──────────────────────────────────────────────────────────────────

    def test_add_car_valid(self):
        car = self.inv.add_car("Toyota", "Supra", 230, condition=100)
        self.assertIsNotNone(car)
        self.assertEqual(car.make, "Toyota")
        self.assertEqual(car.condition, 100)

    def test_add_car_appears_in_race_ready(self):
        car = add_good_car(self.inv)
        ready_ids = [c.car_id for c in self.inv.get_race_ready_cars()]
        self.assertIn(car.car_id, ready_ids)

    def test_get_car_returns_correct_car(self):
        car = add_good_car(self.inv)
        fetched = self.inv.get_car(car.car_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.car_id, car.car_id)

    def test_get_car_unknown_returns_none(self):
        self.assertIsNone(self.inv.get_car("no-such-id"))

    def test_damage_car_reduces_condition(self):
        car = add_good_car(self.inv, condition=100)
        self.inv.damage_car(car.car_id, 20)
        self.assertEqual(self.inv.get_car(car.car_id).condition, 80)

    def test_damage_car_clamps_at_zero(self):
        car = add_good_car(self.inv, condition=10)
        self.inv.damage_car(car.car_id, 50)
        self.assertEqual(self.inv.get_car(car.car_id).condition, 0)

    def test_repair_car_increases_condition(self):
        car = add_good_car(self.inv, condition=40)
        self.inv.repair_car(car.car_id, 30)
        self.assertEqual(self.inv.get_car(car.car_id).condition, 70)

    def test_repair_car_clamps_at_hundred(self):
        car = add_good_car(self.inv, condition=90)
        self.inv.repair_car(car.car_id, 50)
        self.assertEqual(self.inv.get_car(car.car_id).condition, 100)

    def test_race_ready_excludes_low_condition(self):
        car = add_good_car(self.inv, condition=25)
        ready_ids = [c.car_id for c in self.inv.get_race_ready_cars()]
        self.assertNotIn(car.car_id, ready_ids)

    def test_race_ready_boundary_exactly_30(self):
        car = add_good_car(self.inv, condition=30)
        ready_ids = [c.car_id for c in self.inv.get_race_ready_cars()]
        self.assertIn(car.car_id, ready_ids)

    def test_race_ready_excludes_in_use(self):
        car = add_good_car(self.inv)
        self.inv.set_car_in_use(car.car_id, True)
        ready_ids = [c.car_id for c in self.inv.get_race_ready_cars()]
        self.assertNotIn(car.car_id, ready_ids)

    def test_set_car_in_use_toggle(self):
        car = add_good_car(self.inv)
        self.inv.set_car_in_use(car.car_id, True)
        self.assertTrue(self.inv.get_car(car.car_id).is_in_use)
        self.inv.set_car_in_use(car.car_id, False)
        self.assertFalse(self.inv.get_car(car.car_id).is_in_use)

    # ── Items ─────────────────────────────────────────────────────────────────

    def test_add_item_valid(self):
        item = self.inv.add_item("Nitrous Kit", "spare_part", quantity=3)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.category, "spare_part")

    def test_consume_item_reduces_quantity(self):
        item = self.inv.add_item("Oil", "consumable", quantity=5)
        self.inv.consume_item(item.item_id, 2)
        # Re-fetch via internal state — item object is mutated in place
        self.assertEqual(item.quantity, 3)

    def test_consume_item_all_quantity(self):
        item = self.inv.add_item("Tyre", "spare_part", quantity=2)
        self.inv.consume_item(item.item_id, 2)
        self.assertEqual(item.quantity, 0)

    # ── Error cases ───────────────────────────────────────────────────────────

    def test_credit_negative_raises(self):
        with self.assertRaises(ValueError):
            self.inv.credit(-100.0)

    def test_debit_negative_raises(self):
        with self.assertRaises(ValueError):
            self.inv.debit(-100.0)

    def test_debit_insufficient_funds_raises(self):
        with self.assertRaises(ValueError):
            self.inv.debit(99_999.0)

    def test_add_car_bad_condition_raises(self):
        with self.assertRaises(ValueError):
            self.inv.add_car("Bad", "Car", 100, condition=150)

    def test_add_car_negative_condition_raises(self):
        with self.assertRaises(ValueError):
            self.inv.add_car("Bad", "Car", 100, condition=-1)

    def test_add_item_invalid_category_raises(self):
        with self.assertRaises(ValueError):
            self.inv.add_item("Mystery", "gadget")

    def test_consume_item_insufficient_raises(self):
        item = self.inv.add_item("Bolt", "spare_part", quantity=1)
        with self.assertRaises(ValueError):
            self.inv.consume_item(item.item_id, 5)

    def test_consume_item_unknown_id_raises(self):
        with self.assertRaises(KeyError):
            self.inv.consume_item("no-such-item")

    def test_damage_car_unknown_id_raises(self):
        with self.assertRaises(KeyError):
            self.inv.damage_car("no-such-car", 10)


if __name__ == "__main__":
    unittest.main()
