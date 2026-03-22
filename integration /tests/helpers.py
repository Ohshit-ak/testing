"""
tests/helpers.py
Shared factory functions that build fully-wired module instances and common
fixture objects.  Every TestCase imports from here — no duplicated setup code.
"""

import sys
import os

# Allow imports from the project root regardless of where pytest/unittest runs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from registration import RegistrationModule
from crew_management import CrewManagementModule
from inventory import InventoryModule
from race_management import RaceManagementModule
from results import ResultsModule
from mission_planning import MissionPlanningModule
from intelligence import IntelligenceModule
from finance_tracker import FinanceTrackerModule


# ── Module factory ────────────────────────────────────────────────────────────

def make_modules(starting_cash: float = 50_000.0):
    """
    Return a fully-wired tuple of all 8 modules with fresh state.
    Unpack as:  reg, crew, inv, race, res, miss, intel, fin = make_modules()
    """
    reg   = RegistrationModule()
    crew  = CrewManagementModule(reg)
    inv   = InventoryModule(starting_cash=starting_cash)
    race  = RaceManagementModule(reg, crew, inv)
    res   = ResultsModule(race, crew, inv)
    miss  = MissionPlanningModule(reg, crew, inv)
    intel = IntelligenceModule(reg, crew)
    fin   = FinanceTrackerModule(inv)
    return reg, crew, inv, race, res, miss, intel, fin


# ── Fixture helpers ───────────────────────────────────────────────────────────

def register_driver(reg, crew, name="Alice Driver", skill=7):
    """Register a driver and add a crew profile. Returns the CrewMember."""
    member = reg.register(name, "driver")
    crew.add_profile(member.member_id, skill_level=skill)
    return member


def register_mechanic(reg, crew, name="Bob Mechanic", skill=8):
    member = reg.register(name, "mechanic")
    crew.add_profile(member.member_id, skill_level=skill)
    return member


def register_strategist(reg, crew, name="Carol Strategist", skill=6):
    member = reg.register(name, "strategist")
    crew.add_profile(member.member_id, skill_level=skill)
    return member


def register_scout(reg, crew, name="Dave Scout", skill=7):
    member = reg.register(name, "scout")
    crew.add_profile(member.member_id, skill_level=skill)
    return member


def register_medic(reg, crew, name="Eve Medic", skill=7):
    member = reg.register(name, "medic")
    crew.add_profile(member.member_id, skill_level=skill)
    return member


def add_good_car(inv, make="Toyota", model="Supra", speed=230, condition=100):
    """Add a race-ready car. Returns the Car object."""
    return inv.add_car(make, model, speed, condition=condition)


def run_full_race(reg, crew, inv, race_mgmt, results_mod,
                  prize_pool=10_000.0,
                  driver1_name="Driver One", driver2_name="Driver Two"):
    """
    Register two drivers, create a race, enter both, start, record result.
    Returns (race, result, driver1, driver2, car1, car2).
    """
    d1 = register_driver(reg, crew, name=driver1_name)
    d2 = register_driver(reg, crew, name=driver2_name)
    c1 = add_good_car(inv, make="Ford",   model="Mustang")
    c2 = add_good_car(inv, make="Chevy",  model="Camaro")

    r = race_mgmt.create_race("Night Race", "LA", prize_pool)
    race_mgmt.enter_race(r.race_id, d1.member_id, c1.car_id)
    race_mgmt.enter_race(r.race_id, d2.member_id, c2.car_id)
    race_mgmt.start_race(r.race_id)

    result = results_mod.record_result(r.race_id, [d1.member_id, d2.member_id])
    return r, result, d1, d2, c1, c2
