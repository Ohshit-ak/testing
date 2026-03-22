"""
Module: Inventory
Responsibility: Track cars, spare parts, tools, and cash balance.
Race results and mission costs flow back into this module.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid


@dataclass
class Car:
    car_id: str
    make: str
    model: str
    top_speed: int          # km/h
    condition: int          # 0 (wrecked) – 100 (perfect)
    is_in_use: bool = False

    def __str__(self):
        status = "IN USE" if self.is_in_use else "AVAILABLE"
        return (
            f"[{self.car_id[:8]}] {self.make} {self.model} | "
            f"Top speed: {self.top_speed} km/h | Condition: {self.condition}/100 | {status}"
        )

    @property
    def is_race_ready(self) -> bool:
        return self.condition >= 30 and not self.is_in_use


@dataclass
class InventoryItem:
    item_id: str
    name: str
    category: str        # "spare_part" | "tool" | "consumable"
    quantity: int

    def __str__(self):
        return f"[{self.item_id[:8]}] {self.name} ({self.category}) x{self.quantity}"


class InventoryModule:
    """
    Central store for vehicles, parts/tools, and cash balance.
    Other modules call credit() / debit() to update cash,
    and acquire_car() / damage_car() for vehicle state.
    """

    def __init__(self, starting_cash: float = 10_000.0):
        self._cash: float = starting_cash
        self._cars: Dict[str, Car] = {}
        self._items: Dict[str, InventoryItem] = {}

    # ------------------------------------------------------------------ #
    #  Cash                                                                #
    # ------------------------------------------------------------------ #

    def credit(self, amount: float, reason: str = "") -> None:
        if amount < 0:
            raise ValueError("Credit amount must be positive.")
        self._cash += amount
        print(f"[INVENTORY] +${amount:,.2f}  {reason}  | Balance: ${self._cash:,.2f}")

    def debit(self, amount: float, reason: str = "") -> None:
        if amount < 0:
            raise ValueError("Debit amount must be positive.")
        if amount > self._cash:
            raise ValueError(
                f"Insufficient funds. Need ${amount:,.2f}, have ${self._cash:,.2f}."
            )
        self._cash -= amount
        print(f"[INVENTORY] -${amount:,.2f}  {reason}  | Balance: ${self._cash:,.2f}")

    @property
    def cash_balance(self) -> float:
        return self._cash

    # ------------------------------------------------------------------ #
    #  Cars                                                                #
    # ------------------------------------------------------------------ #

    def add_car(self, make: str, model: str, top_speed: int, condition: int = 100) -> Car:
        if not (0 <= condition <= 100):
            raise ValueError("Condition must be 0–100.")
        car = Car(
            car_id=str(uuid.uuid4()),
            make=make,
            model=model,
            top_speed=top_speed,
            condition=condition,
        )
        self._cars[car.car_id] = car
        print(f"[INVENTORY] Car added: {car}")
        return car

    def damage_car(self, car_id: str, damage: int) -> Car:
        """Reduce a car's condition. Raises if car not found."""
        car = self._get_car_or_raise(car_id)
        car.condition = max(0, car.condition - damage)
        print(f"[INVENTORY] {car.make} {car.model} damaged by {damage} pts → condition {car.condition}/100")
        if car.condition < 30:
            print(f"  ⚠  {car.make} {car.model} needs repair before next race!")
        return car

    def repair_car(self, car_id: str, restore: int = 100) -> Car:
        car = self._get_car_or_raise(car_id)
        car.condition = min(100, car.condition + restore)
        print(f"[INVENTORY] {car.make} {car.model} repaired → condition {car.condition}/100")
        return car

    def set_car_in_use(self, car_id: str, in_use: bool) -> None:
        self._get_car_or_raise(car_id).is_in_use = in_use

    def get_race_ready_cars(self) -> List[Car]:
        return [c for c in self._cars.values() if c.is_race_ready]

    def get_car(self, car_id: str) -> Optional[Car]:
        return self._cars.get(car_id)

    # ------------------------------------------------------------------ #
    #  Parts & Tools                                                       #
    # ------------------------------------------------------------------ #

    def add_item(self, name: str, category: str, quantity: int = 1) -> InventoryItem:
        valid_cats = {"spare_part", "tool", "consumable"}
        if category not in valid_cats:
            raise ValueError(f"Category must be one of {valid_cats}.")
        item = InventoryItem(
            item_id=str(uuid.uuid4()),
            name=name,
            category=category,
            quantity=quantity,
        )
        self._items[item.item_id] = item
        print(f"[INVENTORY] Item added: {item}")
        return item

    def consume_item(self, item_id: str, qty: int = 1) -> None:
        item = self._items.get(item_id)
        if item is None:
            raise KeyError(f"Item '{item_id}' not found.")
        if item.quantity < qty:
            raise ValueError(f"Not enough '{item.name}' (have {item.quantity}, need {qty}).")
        item.quantity -= qty
        print(f"[INVENTORY] Used {qty}x '{item.name}' → {item.quantity} remaining.")

    # ------------------------------------------------------------------ #
    #  Display                                                             #
    # ------------------------------------------------------------------ #

    def list_inventory(self) -> None:
        print(f"\n=== INVENTORY  (Cash: ${self._cash:,.2f}) ===")
        print("  -- CARS --")
        if not self._cars:
            print("  (none)")
        for c in self._cars.values():
            print(f"  {c}")
        print("  -- ITEMS --")
        if not self._items:
            print("  (none)")
        for i in self._items.values():
            print(f"  {i}")
        print()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get_car_or_raise(self, car_id: str) -> Car:
        car = self._cars.get(car_id)
        if car is None:
            raise KeyError(f"Car '{car_id}' not in inventory.")
        return car
