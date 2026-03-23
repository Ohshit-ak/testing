"""
StreetRace Manager — Dynamic System Integration
===============================================
Interactive system that allows flexible configuration and operation
of all modules through user input and configuration menus.
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
#  Helper Functions
# ──────────────────────────────────────────────

def section(title: str) -> None:
    """Print a section header."""
    print("\n" + "═" * 60)
    print(f"  {title}")
    print("═" * 60)


def prompt_int(msg: str, min_val: int = None, max_val: int = None) -> int:
    """Prompt user for integer input with optional range validation."""
    while True:
        try:
            val = int(input(msg))
            if min_val is not None and val < min_val:
                print(f"  ✗ Please enter a value >= {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"  ✗ Please enter a value <= {max_val}")
                continue
            return val
        except ValueError:
            print("  ✗ Invalid integer. Try again.")


def prompt_str(msg: str, allow_empty: bool = False) -> str:
    """Prompt user for string input."""
    while True:
        val = input(msg).strip()
        if not val and not allow_empty:
            print("  ✗ Input cannot be empty.")
            continue
        return val


def prompt_yes_no(msg: str) -> bool:
    """Prompt user for yes/no confirmation."""
    while True:
        resp = input(msg).strip().lower()
        if resp in ("y", "yes"):
            return True
        elif resp in ("n", "no"):
            return False
        print("  ✗ Please enter 'y' or 'n'.")


def safe_call(fn):
    """Wrap a function call to catch and report errors gracefully."""
    try:
        fn()
    except (ValueError, KeyError) as e:
        print(f"  ✗ Error: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")





# ──────────────────────────────────────────────
#  System Bootstrap
# ──────────────────────────────────────────────

def build_system(starting_cash: int = 15_000):
    """Instantiate and wire every module."""
    reg   = RegistrationModule()
    crew  = CrewManagementModule(reg)
    inv   = InventoryModule(starting_cash=starting_cash)
    race  = RaceManagementModule(reg, crew, inv)
    res   = ResultsModule(race, crew, inv)
    miss  = MissionPlanningModule(reg, crew, inv)
    intel = IntelligenceModule(reg, crew)
    fin   = FinanceTrackerModule(inv)

    return reg, crew, inv, race, res, miss, intel, fin


# ──────────────────────────────────────────────
#  Registration Menu
# ──────────────────────────────────────────────

def menu_registration(reg):
    """Interactive registration menu."""
    while True:
        section("REGISTRATION MENU")
        print("  1. Register crew member")
        print("  2. List all members")
        print("  3. Back to main menu")
        choice = prompt_int("  Choose: ", 1, 3)

        if choice == 1:
            name = prompt_str("  Member name: ")
            print("    Roles: driver, mechanic, strategist, scout, medic")
            role = prompt_str("  Role: ").lower()
            try:
                member = reg.register(name, role)
                print(f"  ✓ Registered {name} as {role}")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 2:
            reg.list_all()

        elif choice == 3:
            break


# ──────────────────────────────────────────────
#  Crew Management Menu
# ──────────────────────────────────────────────

def menu_crew(crew, reg):
    """Interactive crew management menu."""
    while True:
        section("CREW MANAGEMENT MENU")
        print("  1. Add skill profile to member")
        print("  2. Add specialisation")
        print("  3. Set availability")
        print("  4. List crew")
        print("  5. Back to main menu")
        choice = prompt_int("  Choose: ", 1, 5)

        if choice == 1:
            if not reg.members:
                print("  ✗ No registered members. Register first.")
                continue
            print("  Available members:")
            for i, (mid, member) in enumerate(reg.members.items(), 1):
                print(f"    {i}. {member.name} (ID: {mid})")
            member_num = prompt_int("  Select member #: ", 1, len(reg.members))
            member_id = list(reg.members.keys())[member_num - 1]
            skill = prompt_int("  Skill level (1-10): ", 1, 10)
            try:
                crew.add_profile(member_id, skill)
                print(f"  ✓ Added skill profile")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 2:
            if not reg.members:
                print("  ✗ No registered members. Register first.")
                continue
            print("  Available members:")
            for i, (mid, member) in enumerate(reg.members.items(), 1):
                print(f"    {i}. {member.name} (ID: {mid})")
            member_num = prompt_int("  Select member #: ", 1, len(reg.members))
            member_id = list(reg.members.keys())[member_num - 1]
            spec = prompt_str("  Specialisation (e.g., 'drift', 'drag racing'): ")
            try:
                crew.add_specialisation(member_id, spec)
                print(f"  ✓ Added specialisation")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 3:
            if not reg.members:
                print("  ✗ No registered members. Register first.")
                continue
            print("  Available members:")
            for i, (mid, member) in enumerate(reg.members.items(), 1):
                print(f"    {i}. {member.name} (ID: {mid})")
            member_num = prompt_int("  Select member #: ", 1, len(reg.members))
            member_id = list(reg.members.keys())[member_num - 1]
            avail = prompt_yes_no("  Available? (y/n): ")
            crew.set_availability(member_id, avail)
            print(f"  ✓ Set availability")

        elif choice == 4:
            crew.list_crew()

        elif choice == 5:
            break


# ──────────────────────────────────────────────
#  Inventory Menu
# ──────────────────────────────────────────────

def menu_inventory(inv):
    """Interactive inventory menu."""
    while True:
        section("INVENTORY MENU")
        print("  1. Add car")
        print("  2. Add item/part")
        print("  3. View inventory")
        print("  4. Back to main menu")
        choice = prompt_int("  Choose: ", 1, 4)

        if choice == 1:
            brand = prompt_str("  Car brand: ")
            model = prompt_str("  Car model: ")
            speed = prompt_int("  Top speed (km/h): ", 100, 400)
            condition = prompt_int("  Condition (0-100): ", 0, 100)
            try:
                inv.add_car(brand, model, speed, condition)
                print(f"  ✓ Added car")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 2:
            name = prompt_str("  Item name: ")
            print("    Types: spare_part, tool, consumable")
            item_type = prompt_str("  Item type: ").lower()
            qty = prompt_int("  Quantity: ", 1)
            try:
                inv.add_item(name, item_type, qty)
                print(f"  ✓ Added item")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 3:
            inv.list_inventory()

        elif choice == 4:
            break


# ──────────────────────────────────────────────
#  Race Management Menu
# ──────────────────────────────────────────────

def menu_races(race_mgmt, reg):
    """Interactive race management menu."""
    races = {}
    while True:
        section("RACE MANAGEMENT MENU")
        print("  1. Create new race")
        print("  2. Enter driver into race")
        print("  3. Start race")
        print("  4. View races")
        print("  5. Back to main menu")
        choice = prompt_int("  Choose: ", 1, 5)

        if choice == 1:
            name = prompt_str("  Race name: ")
            location = prompt_str("  Location: ")
            prize = prompt_int("  Prize pool ($): ", 100)
            try:
                race = race_mgmt.create_race(name, location, prize)
                races[race.race_id] = race
                print(f"  ✓ Created race '{name}'")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 2:
            if not races:
                print("  ✗ No races exist. Create one first.")
                continue
            if not reg.members:
                print("  ✗ No registered members.")
                continue
            print("  Available races:")
            for i, (rid, race) in enumerate(races.items(), 1):
                print(f"    {i}. {race.name} (ID: {rid})")
            race_num = prompt_int("  Select race #: ", 1, len(races))
            race_id = list(races.keys())[race_num - 1]

            print("  Available drivers:")
            drivers = [(mid, m) for mid, m in reg.members.items() if m.role == "driver"]
            for i, (mid, member) in enumerate(drivers, 1):
                print(f"    {i}. {member.name} (ID: {mid})")
            if not drivers:
                print("  ✗ No drivers available.")
                continue
            driver_num = prompt_int("  Select driver #: ", 1, len(drivers))
            driver_id = drivers[driver_num - 1][0]

            car_id = prompt_str("  Car ID: ")
            try:
                race_mgmt.enter_race(race_id, driver_id, car_id)
                print(f"  ✓ Entered driver into race")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 3:
            if not races:
                print("  ✗ No races exist.")
                continue
            print("  Available races:")
            for i, (rid, race) in enumerate(races.items(), 1):
                print(f"    {i}. {race.name} (ID: {rid})")
            race_num = prompt_int("  Select race #: ", 1, len(races))
            race_id = list(races.keys())[race_num - 1]
            try:
                race_mgmt.start_race(race_id)
                print(f"  ✓ Race started")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 4:
            race_mgmt.list_races()

        elif choice == 5:
            break


# ──────────────────────────────────────────────
#  Mission Menu
# ──────────────────────────────────────────────

def menu_missions(missions, reg):
    """Interactive mission management menu."""
    active_missions = {}
    while True:
        section("MISSION MENU")
        print("  1. Plan new mission")
        print("  2. Assign member to mission")
        print("  3. Start mission")
        print("  4. Complete mission")
        print("  5. View missions")
        print("  6. Back to main menu")
        choice = prompt_int("  Choose: ", 1, 6)

        if choice == 1:
            print("    Mission types: delivery, rescue, repair_run")
            mission_type = prompt_str("  Mission type: ").lower()
            desc = prompt_str("  Description: ")
            try:
                mission = missions.plan_mission(mission_type, desc)
                active_missions[mission.mission_id] = mission
                print(f"  ✓ Planned mission")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 2:
            if not active_missions:
                print("  ✗ No missions exist. Plan one first.")
                continue
            if not reg.members:
                print("  ✗ No registered members.")
                continue
            print("  Available missions:")
            for i, (mid, m) in enumerate(active_missions.items(), 1):
                print(f"    {i}. {m.description} (ID: {mid})")
            mission_num = prompt_int("  Select mission #: ", 1, len(active_missions))
            mission_id = list(active_missions.keys())[mission_num - 1]

            print("  Available members:")
            for i, (mid, m) in enumerate(reg.members.items(), 1):
                print(f"    {i}. {m.name} (ID: {mid})")
            member_num = prompt_int("  Select member #: ", 1, len(reg.members))
            member_id = list(reg.members.keys())[member_num - 1]

            try:
                missions.assign_member(mission_id, member_id)
                print(f"  ✓ Assigned member to mission")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 3:
            if not active_missions:
                print("  ✗ No missions exist.")
                continue
            print("  Available missions:")
            for i, (mid, m) in enumerate(active_missions.items(), 1):
                print(f"    {i}. {m.description} (ID: {mid})")
            mission_num = prompt_int("  Select mission #: ", 1, len(active_missions))
            mission_id = list(active_missions.keys())[mission_num - 1]
            try:
                missions.start_mission(mission_id)
                print(f"  ✓ Mission started")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 4:
            if not active_missions:
                print("  ✗ No missions exist.")
                continue
            print("  Available missions:")
            for i, (mid, m) in enumerate(active_missions.items(), 1):
                print(f"    {i}. {m.description} (ID: {mid})")
            mission_num = prompt_int("  Select mission #: ", 1, len(active_missions))
            mission_id = list(active_missions.keys())[mission_num - 1]
            success = prompt_yes_no("  Mission successful? (y/n): ")
            try:
                missions.complete_mission(mission_id, success)
                print(f"  ✓ Mission completed")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 5:
            missions.list_missions()

        elif choice == 6:
            break


# ──────────────────────────────────────────────
#  Intelligence Menu
# ──────────────────────────────────────────────

def menu_intelligence(intel, reg):
    """Interactive intelligence menu."""
    reports = {}
    while True:
        section("INTELLIGENCE MENU")
        print("  1. File intelligence report")
        print("  2. Analyse report")
        print("  3. View rivals")
        print("  4. View reports")
        print("  5. Back to main menu")
        choice = prompt_int("  Choose: ", 1, 5)

        if choice == 1:
            if not reg.members:
                print("  ✗ No registered members.")
                continue
            print("  Available scouts:")
            scouts = [(mid, m) for mid, m in reg.members.items() if m.role == "scout"]
            if not scouts:
                print("  ✗ No scouts available.")
                continue
            for i, (mid, member) in enumerate(scouts, 1):
                print(f"    {i}. {member.name} (ID: {mid})")
            scout_num = prompt_int("  Select scout #: ", 1, len(scouts))
            scout_id = scouts[scout_num - 1][0]

            rival = prompt_str("  Rival crew name: ")
            info = prompt_str("  Intelligence info: ")
            try:
                report = intel.file_report(scout_id, rival, info)
                reports[report.report_id] = report
                print(f"  ✓ Report filed")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 2:
            if not reports:
                print("  ✗ No reports exist. File one first.")
                continue
            if not reg.members:
                print("  ✗ No registered members.")
                continue
            print("  Available strategists:")
            strats = [(mid, m) for mid, m in reg.members.items() if m.role == "strategist"]
            if not strats:
                print("  ✗ No strategists available.")
                continue
            for i, (mid, member) in enumerate(strats, 1):
                print(f"    {i}. {member.name} (ID: {mid})")
            strat_num = prompt_int("  Select strategist #: ", 1, len(strats))
            strat_id = strats[strat_num - 1][0]

            print("  Available reports:")
            for i, (rid, r) in enumerate(reports.items(), 1):
                print(f"    {i}. Report on {r.rival_name} (ID: {rid})")
            report_num = prompt_int("  Select report #: ", 1, len(reports))
            report_id = list(reports.keys())[report_num - 1]

            print("    Threat levels: low, medium, high, critical")
            threat = prompt_str("  Threat level: ").lower()
            try:
                intel.analyse_report(strat_id, report_id, threat)
                print(f"  ✓ Report analysed")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 3:
            intel.show_rivals()

        elif choice == 4:
            intel.show_reports()

        elif choice == 5:
            break


# ──────────────────────────────────────────────
#  Finance Menu
# ──────────────────────────────────────────────

def menu_finance(finance):
    """Interactive finance menu."""
    while True:
        section("FINANCE MENU")
        print("  1. Record income")
        print("  2. Record expense")
        print("  3. View ledger")
        print("  4. View summary")
        print("  5. View category breakdown")
        print("  6. Back to main menu")
        choice = prompt_int("  Choose: ", 1, 6)

        if choice == 1:
            amount = prompt_int("  Amount ($): ", 0)
            print("    Categories: sponsorship, winnings, bonus, other")
            category = prompt_str("  Category: ").lower()
            desc = prompt_str("  Description: ")
            try:
                finance.record_income(amount, category, desc)
                print(f"  ✓ Income recorded")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 2:
            amount = prompt_int("  Amount ($): ", 0)
            print("    Categories: equipment, maintenance, fuel, salary, insurance, other")
            category = prompt_str("  Category: ").lower()
            desc = prompt_str("  Description: ")
            try:
                finance.record_expense(amount, category, desc)
                print(f"  ✓ Expense recorded")
            except (ValueError, KeyError) as e:
                print(f"  ✗ Error: {e}")

        elif choice == 3:
            finance.show_ledger()

        elif choice == 4:
            finance.show_summary()

        elif choice == 5:
            finance.show_category_breakdown()

        elif choice == 6:
            break


# ──────────────────────────────────────────────
#  Main Menu & System Loop
# ──────────────────────────────────────────────

def main_menu():
    """Main system menu with dynamic module access."""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  StreetRace Manager — Dynamic System".center(58) + "║")
    print("╚" + "═" * 58 + "╝")

    starting_cash = prompt_int(
        "\nInitial system cash ($) [default 15000]: ",
        min_val=1000
    ) if prompt_yes_no("\nConfigure starting cash? (y/n): ") else 15000

    reg, crew, inv, race_mgmt, results, missions, intel, finance = build_system(starting_cash)

    while True:
        section("MAIN MENU")
        print("  1. Registration")
        print("  2. Crew Management")
        print("  3. Inventory")
        print("  4. Race Management")
        print("  5. Missions")
        print("  6. Intelligence")
        print("  7. Finance")
        print("  8. View System Report")
        print("  9. Exit")
        choice = prompt_int("  Choose: ", 1, 9)

        if choice == 1:
            menu_registration(reg)
        elif choice == 2:
            menu_crew(crew, reg)
        elif choice == 3:
            menu_inventory(inv)
        elif choice == 4:
            menu_races(race_mgmt, reg)
        elif choice == 5:
            menu_missions(missions, reg)
        elif choice == 6:
            menu_intelligence(intel, reg)
        elif choice == 7:
            menu_finance(finance)
        elif choice == 8:
            section("SYSTEM REPORT")
            reg.list_all()
            print()
            crew.list_crew()
            print()
            inv.list_inventory()
            print()
            finance.show_summary()
        elif choice == 9:
            print("\n✅  System shutdown. Goodbye!\n")
            break


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    main_menu()
