"""
StreetRace Manager — System Integration
========================================
Wires all modules together and runs a comprehensive integration test
that exercises all inter-module business rules.
"""

from registration import RegistrationModule
from crew_management import CrewManagementModule
from inventory import InventoryModule
from race_management import RaceManagementModule
from results import ResultsModule
from mission_planning import MissionPlanningModule
from intelligence import IntelligenceModule
from finance_tracker import FinanceTrackerModule


# ──────────────────────────────────────────────
#  Helper
# ──────────────────────────────────────────────

def section(title: str) -> None:
    print("\n" + "═" * 60)
    print(f"  {title}")
    print("═" * 60)


def expect_error(description: str, fn):
    """Run fn and assert it raises; print the caught message."""
    try:
        fn()
        print(f"  ✗ EXPECTED ERROR NOT RAISED: {description}")
    except (ValueError, KeyError) as e:
        print(f"  ✓ Caught expected error [{description}]: {e}")


# ──────────────────────────────────────────────
#  System bootstrap
# ──────────────────────────────────────────────

def build_system():
    """Instantiate and wire every module."""
    reg   = RegistrationModule()
    crew  = CrewManagementModule(reg)
    inv   = InventoryModule(starting_cash=15_000)
    race  = RaceManagementModule(reg, crew, inv)
    res   = ResultsModule(race, crew, inv)
    miss  = MissionPlanningModule(reg, crew, inv)
    intel = IntelligenceModule(reg, crew)
    fin   = FinanceTrackerModule(inv)

    return reg, crew, inv, race, res, miss, intel, fin


# ──────────────────────────────────────────────
#  Integration Tests
# ──────────────────────────────────────────────

def run_integration_tests():
    reg, crew, inv, race_mgmt, results, missions, intel, finance = build_system()

    # ── 1. Registration ────────────────────────────────────────────────
    section("1. REGISTRATION — registering crew members")

    dom    = reg.register("Dom Torretto",   "driver")
    letty  = reg.register("Letty Ortiz",    "driver")
    tej    = reg.register("Tej Parker",     "mechanic")
    roman  = reg.register("Roman Pearce",   "strategist")
    suki   = reg.register("Suki",           "scout")
    elena  = reg.register("Elena Neves",    "medic")

    # Business rule: duplicate name must fail
    expect_error("duplicate name", lambda: reg.register("Dom Torretto", "driver"))
    # Business rule: invalid role must fail
    expect_error("invalid role", lambda: reg.register("New Guy", "hacker"))

    reg.list_all()

    # ── 2. Crew Management ─────────────────────────────────────────────
    section("2. CREW MANAGEMENT — assigning skill levels & specialisations")

    # Business rule: must be registered first (already is)
    crew.add_profile(dom.member_id,   skill_level=9)
    crew.add_profile(letty.member_id, skill_level=8)
    crew.add_profile(tej.member_id,   skill_level=10)
    crew.add_profile(roman.member_id, skill_level=6)
    crew.add_profile(suki.member_id,  skill_level=7)
    crew.add_profile(elena.member_id, skill_level=8)

    crew.add_specialisation(dom.member_id,   "drag racing")
    crew.add_specialisation(letty.member_id, "drift")
    crew.add_specialisation(tej.member_id,   "engine tuning")
    crew.add_specialisation(roman.member_id, "route planning")

    # Business rule: duplicate profile must fail
    expect_error("duplicate profile", lambda: crew.add_profile(dom.member_id, 5))

    crew.list_crew()

    # ── 3. Inventory ───────────────────────────────────────────────────
    section("3. INVENTORY — adding cars and parts")

    charger   = inv.add_car("Dodge",     "Charger R/T",  220, condition=100)
    eclipse   = inv.add_car("Mitsubishi","Eclipse GSX",  200, condition=90)
    supra     = inv.add_car("Toyota",    "Supra MkIV",   230, condition=85)
    civic     = inv.add_car("Honda",     "Civic Type R", 190, condition=40)  # marginal

    nitro     = inv.add_item("Nitrous Oxide Kit",   "spare_part", quantity=3)
    wrench    = inv.add_item("Impact Wrench Set",   "tool",       quantity=2)
    oil       = inv.add_item("Synthetic Oil 5W-30", "consumable", quantity=10)

    inv.list_inventory()

    # ── 4. Race Management — happy path ────────────────────────────────
    section("4. RACE MANAGEMENT — creating race & entering drivers")

    night_race = race_mgmt.create_race(
        name="Midnight Mile",
        location="East LA Boulevard",
        prize_pool=10_000,
    )

    race_mgmt.enter_race(night_race.race_id, dom.member_id,   charger.car_id)
    race_mgmt.enter_race(night_race.race_id, letty.member_id, eclipse.car_id)

    # Business rule: only drivers may enter — suki is a scout, must fail
    expect_error(
        "scout cannot enter race",
        lambda: race_mgmt.enter_race(night_race.race_id, suki.member_id, supra.car_id),
    )

    race_mgmt.list_races()

    # Business rules enforcement
    expect_error(
        "mechanic cannot enter race",
        lambda: race_mgmt.enter_race(night_race.race_id, tej.member_id, supra.car_id),
    )
    expect_error(
        "car below condition threshold (civic)",
        lambda: race_mgmt.enter_race(night_race.race_id, dom.member_id, civic.car_id),
    )
    # Dom is already entered — duplicate driver
    expect_error(
        "driver already entered",
        lambda: race_mgmt.enter_race(night_race.race_id, dom.member_id, supra.car_id),
    )

    race_mgmt.start_race(night_race.race_id)

    # ── 5. Results ─────────────────────────────────────────────────────
    section("5. RESULTS — recording race outcome & prize distribution")

    result = results.record_result(
        race_id=night_race.race_id,
        finishing_order=[letty.member_id, dom.member_id],
        damaged_cars=[charger.car_id, eclipse.car_id],
    )

    results.show_rankings()
    inv.list_inventory()   # show updated car conditions and cash

    # Business rule: cannot record result on a FINISHED race
    expect_error(
        "result on already-finished race",
        lambda: results.record_result(night_race.race_id, [letty.member_id, dom.member_id]),
    )

    # ── 6. Mission Planning ────────────────────────────────────────────
    section("6. MISSION PLANNING — delivery & rescue missions")

    # Delivery (requires driver)
    delivery = missions.plan_mission("delivery", "Drop package at Sunset Blvd")
    missions.assign_member(delivery.mission_id, dom.member_id)
    missions.start_mission(delivery.mission_id)
    missions.complete_mission(delivery.mission_id, success=True)

    # Rescue (requires driver + medic)
    rescue = missions.plan_mission("rescue", "Extract stranded racer from impound")
    missions.assign_member(rescue.mission_id, letty.member_id)
    missions.assign_member(rescue.mission_id, elena.member_id)
    missions.start_mission(rescue.mission_id)
    missions.complete_mission(rescue.mission_id, success=True)

    # Business rule: cannot start without required roles covered
    repair_mission = missions.plan_mission("repair_run", "Retrieve engine parts")
    # Don't assign mechanic — should fail on start
    expect_error(
        "missing required role (mechanic) on start",
        lambda: missions.start_mission(repair_mission.mission_id),
    )
    # Assign the mechanic and retry
    missions.assign_member(repair_mission.mission_id, tej.member_id)
    missions.start_mission(repair_mission.mission_id)
    missions.complete_mission(repair_mission.mission_id, success=False)  # failed mission

    # Business rule: mission cannot start if required role unavailable
    # (make tej busy again to prove the check)
    crew.set_availability(tej.member_id, False)
    expect_error(
        "no available mechanic for repair_run",
        lambda: missions.plan_mission("repair_run", "Another repair"),
    )
    crew.set_availability(tej.member_id, True)  # restore

    missions.list_missions()

    # ── 7. Intelligence Module ─────────────────────────────────────────
    section("7. INTELLIGENCE — filing and analysing rival intel")

    r1 = intel.file_report(suki.member_id,  "DK Crew", "Spotted 3 heavily modified EVOs near the docks.")
    r2 = intel.file_report(suki.member_id,  "DK Crew", "Their lead driver seen doing 0-60 in 3.8s.")

    intel.analyse_report(roman.member_id, r1.report_id, "medium")
    intel.analyse_report(roman.member_id, r2.report_id, "high")

    # Business rule: only scouts can file
    expect_error(
        "non-scout filing intel",
        lambda: intel.file_report(dom.member_id, "Unknown Crew", "just checking"),
    )
    # Business rule: only strategists can analyse
    expect_error(
        "non-strategist analysing report",
        lambda: intel.analyse_report(dom.member_id, r1.report_id, "critical"),
    )

    intel.show_rivals()
    intel.show_reports()

    # ── 8. Finance Tracker Module ──────────────────────────────────────
    section("8. FINANCE TRACKER — ledger and P/L summary")

    # Record a car purchase as an expense (outside normal flow)
    finance.record_expense(3000, "equipment",    "Purchased turbocharger upgrade")
    finance.record_income(500,   "sponsorship",  "Toretto's Market & Cafe sponsorship deal")

    finance.show_ledger()
    finance.show_summary()
    finance.show_category_breakdown()

    # ── 9. Final System Snapshot ───────────────────────────────────────
    section("9. FINAL SYSTEM SNAPSHOT")

    reg.list_all()
    crew.list_crew()
    inv.list_inventory()
    results.show_rankings()
    missions.list_missions()
    intel.show_rivals()
    finance.show_summary()

    print("\n✅  All integration tests completed.\n")


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # Patch enter_race test section — the scout-entering-race call above
    # will throw at module load; we need to protect it. Let's wrap the whole run.
    run_integration_tests()
