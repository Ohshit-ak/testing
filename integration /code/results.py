"""
Module: Results
Responsibility: Record race outcomes, update rankings, handle prize money.
Depends on: RaceManagementModule, CrewManagementModule, InventoryModule.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import uuid

from race_management import RaceManagementModule
from crew_management import CrewManagementModule
from inventory import InventoryModule


PRIZE_SPLIT = {1: 0.50, 2: 0.30, 3: 0.20}   # 1st gets 50%, 2nd 30%, 3rd 20%
DAMAGE_PER_RACE = 15                           # condition points lost per race


@dataclass
class RaceResult:
    result_id: str
    race_id: str
    race_name: str
    finishing_order: List[str]        # ordered list of driver_ids
    prizes_awarded: Dict[str, float]  # driver_id -> prize $
    damage_events: List[Tuple[str, int]] = field(default_factory=list)  # (car_id, pts)


@dataclass
class DriverRanking:
    driver_id: str
    driver_name: str
    total_races: int = 0
    wins: int = 0
    podiums: int = 0
    total_prize: float = 0.0

    @property
    def win_rate(self) -> float:
        return (self.wins / self.total_races * 100) if self.total_races else 0.0

    def __str__(self):
        return (
            f"{self.driver_name} | Races: {self.total_races} | "
            f"Wins: {self.wins} | Podiums: {self.podiums} | "
            f"Earnings: ${self.total_prize:,.2f} | Win rate: {self.win_rate:.1f}%"
        )


class ResultsModule:
    """
    Finalises a race:
      - Verifies race is IN_PROGRESS.
      - Distributes prize money to winning drivers via InventoryModule.
      - Applies car damage to InventoryModule.
      - Updates driver stats in CrewManagementModule.
      - Marks race as FINISHED and frees up drivers/cars.
    """

    def __init__(
        self,
        race_mgmt: RaceManagementModule,
        crew: CrewManagementModule,
        inventory: InventoryModule,
    ):
        self._race_mgmt = race_mgmt
        self._crew = crew
        self._inv = inventory
        self._results: Dict[str, RaceResult] = {}
        self._rankings: Dict[str, DriverRanking] = {}  # driver_id -> DriverRanking

    # ------------------------------------------------------------------ #
    #  Recording results                                                   #
    # ------------------------------------------------------------------ #

    def record_result(
        self,
        race_id: str,
        finishing_order: List[str],   # driver_ids in 1st→last order
        damaged_cars: Optional[List[str]] = None,  # list of car_ids
    ) -> RaceResult:
        """
        Finalise a race.
        finishing_order must contain all driver_ids entered in the race.
        """
        race = self._race_mgmt.get_race(race_id)
        if race is None:
            raise KeyError(f"Race '{race_id}' not found.")
        if race.status != "IN_PROGRESS":
            raise ValueError(
                f"Race '{race.name}' is not in progress (status: {race.status})."
            )

        # Validate finishing_order matches entries
        entries = self._race_mgmt.get_active_entries(race_id)
        entered_drivers = {e[0] for e in entries}
        if set(finishing_order) != entered_drivers:
            raise ValueError(
                "finishing_order must include exactly the drivers entered in the race."
            )

        # ---- Distribute prize money ----------------------------------- #
        prizes: Dict[str, float] = {}
        for position, driver_id in enumerate(finishing_order, start=1):
            split = PRIZE_SPLIT.get(position, 0.0)
            prize = race.prize_pool * split
            prizes[driver_id] = prize
            if prize > 0:
                reg_member = self._race_mgmt._reg.get_member(driver_id)
                name = reg_member.name if reg_member else driver_id
                self._inv.credit(prize, reason=f"Race prize – {name} (P{position})")

        # ---- Apply car damage ----------------------------------------- #
        damage_events: List[Tuple[str, int]] = []
        cars_to_damage = damaged_cars if damaged_cars else [e[1] for e in entries]
        for car_id in cars_to_damage:
            self._inv.damage_car(car_id, DAMAGE_PER_RACE)
            damage_events.append((car_id, DAMAGE_PER_RACE))

        # ---- Update driver stats -------------------------------------- #
        for position, driver_id in enumerate(finishing_order, start=1):
            self._crew.record_race(driver_id)
            ranking = self._rankings.setdefault(
                driver_id,
                DriverRanking(
                    driver_id=driver_id,
                    driver_name=(
                        self._race_mgmt._reg.get_member(driver_id).name
                        if self._race_mgmt._reg.get_member(driver_id) else driver_id
                    ),
                ),
            )
            ranking.total_races += 1
            ranking.total_prize += prizes.get(driver_id, 0.0)
            if position == 1:
                ranking.wins += 1
            if position <= 3:
                ranking.podiums += 1

        # ---- Free up resources --------------------------------------- #
        race.status = "FINISHED"
        for driver_id, car_id in entries:
            self._crew.set_availability(driver_id, True)
            self._inv.set_car_in_use(car_id, False)

        # ---- Save result --------------------------------------------- #
        result = RaceResult(
            result_id=str(uuid.uuid4()),
            race_id=race_id,
            race_name=race.name,
            finishing_order=finishing_order,
            prizes_awarded=prizes,
            damage_events=damage_events,
        )
        self._results[result.result_id] = result

        self._print_podium(race.name, finishing_order, prizes)
        return result

    # ------------------------------------------------------------------ #
    #  Display                                                             #
    # ------------------------------------------------------------------ #

    def show_rankings(self) -> None:
        print("\n=== DRIVER RANKINGS ===")
        if not self._rankings:
            print("  (no results recorded yet)")
            return
        sorted_drivers = sorted(
            self._rankings.values(),
            key=lambda r: (-r.wins, -r.podiums, -r.total_prize),
        )
        for i, dr in enumerate(sorted_drivers, 1):
            print(f"  #{i} {dr}")
        print()

    def show_result(self, result_id: str) -> None:
        result = self._results.get(result_id)
        if result is None:
            print(f"Result '{result_id}' not found.")
            return
        print(f"\n=== RESULT: {result.race_name} ===")
        for pos, driver_id in enumerate(result.finishing_order, 1):
            m = self._race_mgmt._reg.get_member(driver_id)
            name = m.name if m else driver_id
            prize = result.prizes_awarded.get(driver_id, 0.0)
            print(f"  P{pos}: {name}  Prize: ${prize:,.2f}")
        print()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _print_podium(
        self, race_name: str, order: List[str], prizes: Dict[str, float]
    ) -> None:
        print(f"\n🏆  RACE FINISHED: {race_name}")
        medals = ["🥇", "🥈", "🥉"]
        for i, driver_id in enumerate(order[:3]):
            m = self._race_mgmt._reg.get_member(driver_id)
            name = m.name if m else driver_id
            prize = prizes.get(driver_id, 0.0)
            print(f"  {medals[i]} P{i+1}: {name}  +${prize:,.2f}")
        print()
