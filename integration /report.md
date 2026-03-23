# Test Case Report: Underground Racing Crew Management System

**Project:** Underground Racing Crew Management System
**Modules Tested:** Registration, Race Management, Results, Mission Planning, Crew Management, Inventory, Intelligence, Finance Tracker
**Test Files Reviewed:** `test_registration.py`, `test_race_management.py`, `test_results.py`, `test_mission_planning.py`, `test_crew_management.py`, `test_inventory.py`, `test_intelligence.py`, `test_finance_tracker.py`, `test_integration.py`

---

## Overview

This report covers four key testing scenarios drawn from the system's test suite:

1. Registering a driver and entering them into a race
2. Attempting to enter a race without a registered (or eligible) driver
3. Completing a race and verifying that results and prize money update the inventory
4. Assigning a mission and validating crew role requirements

Each section explains the purpose of the test, what it checks, and any errors or issues identified.

---

## 1. Registering a Driver and Entering Them Into a Race

### What This Tests

Before a driver can compete, they must be registered in the system with a valid name and role, and then have a crew profile created. Only after both steps are complete can they enter a race. These tests confirm the full happy path works correctly end-to-end.

### Relevant Test Cases

**`test_register_valid_driver`** (`test_registration.py`)
Registers a crew member with the role "driver" and confirms the returned object has the correct name, role, and active status. This is the most fundamental test in the suite — nothing else works if registration is broken.

**`test_add_profile_valid`** (`test_crew_management.py`)
After registration, a crew profile must be created via `CrewManagementModule`. This test confirms the profile is stored correctly and has the expected skill level. Without a profile, the member cannot participate in races or missions.

**`test_enter_race_valid_driver`** (`test_race_management.py`)
Creates a race, then enters a registered driver with a race-ready car. Confirms the entry appears in the race's entry list. This validates the core flow a player would follow every session.

**`test_enter_race_marks_driver_unavailable`** (`test_race_management.py`)
Once a driver enters a race, they should be marked as busy so they cannot be double-booked. This test confirms the availability flag is set to `False` on entry.

**`test_enter_race_marks_car_in_use`** (`test_race_management.py`)
Similarly, the car must be flagged as in-use to prevent the same vehicle appearing in two races simultaneously. This test checks `is_in_use` is set to `True`.

### Errors Detected

No failures were found in this flow. However, one structural observation: `test_finance_tracker.py` has a duplicated `setUp` block that calls `make_modules()` twice, discarding the first result. While this does not break tests, it wastes resources and could cause confusion:

```python
# In TestFinanceTracker.setUp — the first unpacking is immediately overwritten
*_, self.inv, _, _, _, _, self.fin = make_modules(starting_cash=5_000.0)
mods = make_modules(starting_cash=5_000.0)  # second call overwrites the first
self.inv = mods[2]
self.fin = mods[7]
```

**Fix:** Remove the first `make_modules()` call and the starred unpacking line, keeping only the second assignment.

---

## 2. Attempting to Enter a Race Without a Registered Driver

### What This Tests

The system must reject invalid attempts to enter a race — whether the person is unregistered, has been deactivated, has the wrong role, is already busy, or is trying to use an unfit car. These guard tests are critical for data integrity; without them, bad state can silently corrupt the simulation.

### Relevant Test Cases

**`test_unregistered_member_cannot_get_crew_profile`** (`test_integration.py`)
Tries to create a crew profile for a randomly generated (non-existent) member ID. Expects a `ValueError`. This confirms that `CrewManagementModule` always verifies identity with `RegistrationModule` before acting.

**`test_deactivated_member_cannot_enter_race`** (`test_integration.py`)
Registers a driver, deactivates them, then tries to enter them in a race. Expects a `ValueError`. Deactivation is a soft-delete — the record exists but the member should be treated as absent from all active operations.

**`test_enter_race_non_driver_raises`** (`test_race_management.py`)
Registers a mechanic and attempts to enter them in a race. Expects a `ValueError`. Races are exclusively for drivers; other roles exist to support, not compete.

**`test_only_driver_can_enter_race`** / **`test_scout_cannot_enter_race`** (`test_integration.py`)
Broader role-enforcement checks confirming mechanics and scouts cannot enter races regardless of how the request is made.

**`test_enter_race_low_condition_car_raises`** (`test_race_management.py`)
Tries to enter a car with condition 20 (below the minimum threshold of 30). Expects a `ValueError`. A damaged car is a safety hazard and a competitive disadvantage — the system must block it.

**`test_enter_race_car_in_use_raises`** (`test_race_management.py`)
Tries to enter a car that is already marked as in-use. Expects a `ValueError`.

**`test_enter_race_duplicate_driver_raises`** and **`test_enter_race_duplicate_car_raises`** (`test_race_management.py`)
Confirms the same driver or the same car cannot appear twice in one race.

**`test_enter_race_unavailable_driver_raises`** (`test_race_management.py`)
A driver manually marked as unavailable (e.g., already on a mission) cannot enter a race.

**`test_start_race_requires_two_entries`** (`test_race_management.py`)
Starting a race with only one driver raises a `ValueError`. A race needs at least two competitors.

**`test_enter_closed_race_raises`** (`test_race_management.py`)
Once a race is `IN_PROGRESS`, no new entries are accepted.

### Errors Detected

No logic errors were found. All guard conditions raise the correct exception types. The role-check in `RaceManagementModule.enter_race` correctly combines a member-existence check, an active-status check, a role check, and an availability check in sequence — this ordering matters because checking availability before confirming the member exists would cause a confusing `KeyError` rather than a clear `ValueError`.

---

## 3. Completing a Race and Verifying Results and Prize Money Update the Inventory

### What This Tests

When a race finishes, several things must happen atomically: prizes must be distributed to the correct drivers based on finishing position, cars must be damaged, driver statistics must be updated, and all locked resources (drivers, cars) must be freed. This section verifies all of these outcomes.

### Relevant Test Cases

**`test_record_result_sets_finished`** (`test_results.py`)
After calling `record_result()`, the race's status must become `"FINISHED"`. This is the gate that prevents double-results.

**`test_first_place_prize_credited`** (`test_results.py`)
The total cash credited to inventory should equal the sum of 1st place (50%) and 2nd place (30%) prizes. The 3rd-place prize is only distributed if there are three or more finishers.

**`test_first_place_gets_50_percent`** and **`test_second_place_gets_30_percent`** (`test_results.py`)
Individually checks the prize split constants: P1 receives 50%, P2 receives 30% of the prize pool.

**`test_race_result_updates_cash_balance`** (`test_integration.py`)
An integration-level check confirming the inventory's cash balance increases by the expected prize total after a race result is recorded. This confirms the chain: `ResultsModule` → `InventoryModule.credit()` → `cash_balance` property.

**`test_car_condition_reduced_by_damage_constant`** (`test_results.py`)
After a race, the car's condition must drop by exactly `DAMAGE_PER_RACE` (15 points). This test catches any accidental change to the damage constant or the damage calculation logic.

**`test_damaged_car_blocks_next_race_entry`** (`test_integration.py`)
A car starting at condition 35 loses 15 points in the race, dropping to 20 — below the 30-point threshold. The test then confirms this car cannot be entered in a second race. This is the key end-to-end consequence of race damage.

**`test_drivers_freed_after_result`** and **`test_cars_released_after_result`** (`test_results.py`)
After the race completes, drivers must be marked available again and cars must have `is_in_use` set back to `False`. Without this, the entire roster would gradually lock up.

**`test_winner_ranking_updated`** and **`test_second_place_has_zero_wins`** (`test_results.py`)
Driver stats in `ResultsModule._rankings` must reflect: 1 win for P1, 0 wins for P2, 1 podium for both.

**`test_race_count_incremented_for_both_drivers`** (`test_results.py`)
`CrewManagementModule` profiles must show `race_count = 1` for each driver after the race, confirming `record_race()` was called correctly.

**`test_no_double_result_on_finished_race`** (`test_results.py`)
Calling `record_result()` on an already-finished race must raise a `ValueError`. Without this guard, prize money could be credited multiple times.

### Errors Detected

No logic errors were found in the results pipeline. One design note worth flagging: `ResultsModule` accesses `self._race_mgmt._reg` (a private attribute) to look up driver names. This is a tight coupling between two modules that could break if `RaceManagementModule`'s internals are refactored. A cleaner approach would be to pass the `RegistrationModule` reference directly to `ResultsModule`, but this is a design concern rather than a bug.

---

## 4. Assigning a Mission and Ensuring Correct Crew Roles Are Validated

### What This Tests

Missions require specific roles to be present and available. The system must refuse to plan or start a mission if the needed crew aren't there, and must refuse to assign the wrong role to a mission slot. These tests protect the simulation from invalid states where missions run without the right people.

### Relevant Test Cases

**`test_plan_delivery_with_driver_available`** (`test_mission_planning.py`)
The baseline happy path: one driver is available, a delivery mission is planned. Confirms the mission is created in `PENDING` status.

**`test_plan_rescue_requires_driver_and_medic`** (`test_mission_planning.py`)
A rescue mission requires both a driver and a medic. This test registers both and confirms planning succeeds. The multi-role requirement is defined in `MISSION_TYPES` and validated during `plan_mission()`.

**`test_plan_mission_no_available_driver_raises`** (`test_mission_planning.py`)
With no drivers registered at all, attempting to plan a delivery mission raises a `ValueError`. The system checks role availability before creating the mission object.

**`test_plan_rescue_no_medic_raises`** (`test_mission_planning.py`) and **`test_mission_blocked_when_no_medic_registered`** (`test_integration.py`)
Even if a driver is available, a rescue mission cannot be planned without a medic. This enforces the multi-role constraint at plan time, not just at start time.

**`test_mission_blocked_when_required_role_unavailable`** (`test_integration.py`)
If the only mechanic is marked as busy (already on another task), a `repair_run` cannot be planned. This confirms that availability — not just existence — is checked.

**`test_assign_wrong_role_raises`** (`test_mission_planning.py`)
Attempting to assign a mechanic to a delivery mission (which needs a driver) raises a `ValueError`. Members can only be assigned to missions their role supports.

**`test_assign_unavailable_member_raises`** (`test_mission_planning.py`)
A member who is marked unavailable cannot be assigned, even if their role matches.

**`test_start_mission_missing_role_raises`** (`test_mission_planning.py`)
A mission can be planned (as `PENDING`) even without members assigned, but it cannot be started until all required roles are covered. This test plans a delivery mission, assigns nobody, and confirms `start_mission()` raises a `ValueError`.

**`test_assign_member_to_delivery`** and **`test_assign_marks_member_unavailable`** (`test_mission_planning.py`)
Once a member is successfully assigned, they appear in `mission.assigned_members` and their availability is set to `False`.

**`test_complete_mission_frees_members`** (`test_mission_planning.py`)
After mission completion, members must be freed (availability restored to `True`) regardless of success or failure.

**`test_driver_busy_in_race_cannot_take_mission`** (`test_integration.py`)
A driver already entered in a race is unavailable and must be blocked from being assigned to a mission simultaneously. This cross-module test confirms that the single shared availability flag correctly prevents double-booking.

### Errors Detected

No logic errors were found. One behavioural note: `abort_mission()` only works on `PENDING` missions — an `IN_PROGRESS` mission cannot be aborted (it must be completed as success or failure). The test `test_abort_in_progress_mission_raises` confirms this guard. This is intentional by design, but could be a surprise to users who expect to cancel a running mission.

---

## Summary of Issues Found

| # | Location | Issue | Severity | Fix |
|---|----------|--------|----------|-----|
| 1 | `test_finance_tracker.py` — `setUp` | `make_modules()` called twice; first call's result is immediately discarded | Low (no test failures, just wasteful) | Remove the first call and starred-unpack line; keep only the second `mods = make_modules(...)` block |
| 2 | `results.py` — `ResultsModule` | Accesses `self._race_mgmt._reg` (private attribute) to resolve driver names | Design / low | Pass `RegistrationModule` directly to `ResultsModule.__init__` as a named parameter |

All other test cases pass as expected. The module dependency chain (Registration → Crew → Inventory → Race/Mission/Results → Intelligence/Finance) is correctly enforced throughout, and all role, availability, and state-transition guards behave as intended.

---

*Report generated from static code and test review. No runtime test execution was performed.*