"""
Module: Race Management
Responsibility: Create races, validate driver + car eligibility, manage race state.
Depends on: RegistrationModule, CrewManagementModule, InventoryModule.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import uuid

from registration import RegistrationModule
from crew_management import CrewManagementModule
from inventory import InventoryModule, Car


@dataclass
class RaceEntry:
    driver_id: str
    car_id: str


@dataclass
class Race:
    race_id: str
    name: str
    location: str
    prize_pool: float
    entries: List[RaceEntry] = field(default_factory=list)
    status: str = "OPEN"       # OPEN | IN_PROGRESS | FINISHED | CANCELLED

    def __str__(self):
        return (
            f"[{self.race_id[:8]}] {self.name} @ {self.location} | "
            f"Prize: ${self.prize_pool:,.2f} | Status: {self.status} | "
            f"Entries: {len(self.entries)}"
        )


class RaceManagementModule:
    """
    Manages the lifecycle of a race: creation → entry → start.
    Enforces:
      - Only drivers may enter.
      - Only race-ready cars may be entered.
      - Cars and drivers are marked busy once committed to a race.
    """

    def __init__(
        self,
        registration: RegistrationModule,
        crew: CrewManagementModule,
        inventory: InventoryModule,
    ):
        self._reg = registration
        self._crew = crew
        self._inv = inventory
        self._races: Dict[str, Race] = {}

    # ------------------------------------------------------------------ #
    #  Race lifecycle                                                      #
    # ------------------------------------------------------------------ #

    def create_race(self, name: str, location: str, prize_pool: float) -> Race:
        if prize_pool < 0:
            raise ValueError("Prize pool cannot be negative.")
        race = Race(
            race_id=str(uuid.uuid4()),
            name=name,
            location=location,
            prize_pool=prize_pool,
        )
        self._races[race.race_id] = race
        print(f"[RACE] Race created: {race}")
        return race

    def enter_race(self, race_id: str, driver_id: str, car_id: str) -> None:
        """Enter a driver + car into an open race."""
        race = self._get_race_or_raise(race_id)
        if race.status != "OPEN":
            raise ValueError(f"Race '{race.name}' is not open for entries (status: {race.status}).")

        # Validate driver
        driver = self._reg.get_member(driver_id)
        if driver is None or not driver.is_active:
            raise ValueError(f"Driver '{driver_id}' is not registered / active.")
        if driver.role != "driver":
            raise ValueError(
                f"'{driver.name}' has role '{driver.role}' — only drivers may enter races."
            )
        if not self._crew.is_available(driver_id):
            raise ValueError(f"Driver '{driver.name}' is currently unavailable.")

        # Validate car
        car = self._inv.get_car(car_id)
        if car is None:
            raise KeyError(f"Car '{car_id}' not found in inventory.")
        if not car.is_race_ready:
            raise ValueError(
                f"Car '{car.make} {car.model}' is not race-ready "
                f"(condition {car.condition}/100 or already in use)."
            )

        # Prevent duplicate entries
        for entry in race.entries:
            if entry.driver_id == driver_id:
                raise ValueError(f"Driver '{driver.name}' is already entered in this race.")
            if entry.car_id == car_id:
                raise ValueError(f"Car '{car.make} {car.model}' is already entered in this race.")

        race.entries.append(RaceEntry(driver_id=driver_id, car_id=car_id))
        self._crew.set_availability(driver_id, False)
        self._inv.set_car_in_use(car_id, True)
        print(f"[RACE] ✓ {driver.name} entered '{race.name}' with {car.make} {car.model}.")

    def start_race(self, race_id: str) -> None:
        race = self._get_race_or_raise(race_id)
        if race.status != "OPEN":
            raise ValueError(f"Race cannot be started (status: {race.status}).")
        if len(race.entries) < 2:
            raise ValueError("A race needs at least 2 entries to start.")
        race.status = "IN_PROGRESS"
        print(f"[RACE] 🏁 Race '{race.name}' has STARTED with {len(race.entries)} drivers!")

    def cancel_race(self, race_id: str) -> None:
        race = self._get_race_or_raise(race_id)
        if race.status == "FINISHED":
            raise ValueError("Cannot cancel a finished race.")
        race.status = "CANCELLED"
        self._free_entries(race)
        print(f"[RACE] Race '{race.name}' CANCELLED. Drivers and cars released.")

    # ------------------------------------------------------------------ #
    #  Queries                                                             #
    # ------------------------------------------------------------------ #

    def get_race(self, race_id: str) -> Optional[Race]:
        return self._races.get(race_id)

    def list_races(self) -> None:
        print("\n=== RACES ===")
        if not self._races:
            print("  (no races created)")
        for r in self._races.values():
            print(f"  {r}")
            for e in r.entries:
                member = self._reg.get_member(e.driver_id)
                car = self._inv.get_car(e.car_id)
                m_name = member.name if member else e.driver_id
                c_name = f"{car.make} {car.model}" if car else e.car_id
                print(f"    → {m_name} driving {c_name}")
        print()

    def get_active_entries(self, race_id: str) -> List[Tuple[str, str]]:
        """Return list of (driver_id, car_id) for the race."""
        race = self._get_race_or_raise(race_id)
        return [(e.driver_id, e.car_id) for e in race.entries]

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get_race_or_raise(self, race_id: str) -> Race:
        race = self._races.get(race_id)
        if race is None:
            raise KeyError(f"Race '{race_id}' not found.")
        return race

    def _free_entries(self, race: Race) -> None:
        for entry in race.entries:
            self._crew.set_availability(entry.driver_id, True)
            self._inv.set_car_in_use(entry.car_id, False)
