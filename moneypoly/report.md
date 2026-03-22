
### ITERATION 1: Linting and Documentation

## File-by-file adds/removals vs original
- `bank.py`
	- Removed: `import math`; `from moneypoly.config import BANK_STARTING_FUNDS`.
	- Added: module docstring; `from config import BANK_STARTING_FUNDS`; class docstring on `Bank`.
- `board.py`
	- Removed: imports via `moneypoly.property` and `moneypoly.config`.
	- Added: module docstring; direct imports `from property import Property, PropertyGroup` and `from config import ...`; changed `prop.is_mortgaged == True` to `prop.is_mortgaged is True` in `is_purchasable`.
- `cards.py`
	- Added: module docstring.
	- Changed formatting/text of card lists (CHANCE, COMMUNITY_CHEST) — spacing/wording normalized; actions/values unchanged.
- `dice.py`
	- Removed: `from moneypoly.config import BOARD_SIZE` (unused).
	- Added: module docstring; `doubles_streak = 0` initialization in `__init__` before `reset()`.
- `game.py`
	- Removed: `import os`, `GO_TO_JAIL_POSITION` import, and all `moneypoly.`-prefixed imports.
	- Minor tweaks: `ui.print_banner("GAME OVER")` (no f-string); simplified conditionals in `interactive_menu` and range checks for menu selections.

- `player.py`
	- Removed: `import sys`; `moneypoly.`-prefixed config import; unused `old_position` variable in `move`.
    - Added: docstrings for all public methods in `Player` class.
- `property.py`
	- Added: module docstring; pylint disables on class and `__init__`; docstring on `PropertyGroup`.
	- Changed: `unmortgage` simplified (removed unnecessary `else`, same behavior).
- `ui.py`
	- Added: module docstring.
	- Changed: `safe_int_input` now catches `ValueError` instead of bare `except`.
- `main.py`
	- Added: module docstring; docstrings for `get_player_names` and `main`.


### ITERATION 2: Linting and Documentation part 2

## File-by-file adds/removals vs original

- `player.py`
    - Added: module docstring; direct config import; pylint disable for `too-many-instance-attributes` on class.
- `property.py`
    - Added: module docstring; pylint disables on class and `__init__`; docstring on `PropertyGroup`.
    - Changed: `unmortgage` simplified (removed unnecessary `else`, same behavior).
    - Added: module docstring; direct config import; pylint disable for `too-many-arguments` on class.
-  `game.py`
    - Added: module docstring; direct imports from local modules; pylint disables (`too-many-instance-attributes` on class, `too-many-branches` on `_move_and_resolve` and `_apply_card`).
### ITERATION 3: Final Linting and Documentation

## File-by-file adds/removals vs original
 - `bank.py`
     - changed config to .config (direct import).
 - `board.py`
     - changed config to .config (direct import).
	 - changed property imports to direct imports from local modules.
 - `game.py`
	 - changed imports to direct imports from local modules.
 - `player.py`
	 - changed config import to direct import from local module.
	 


## Notes
- No gameplay logic changed; only lint suppressions and documentation were added to achieve pylint 10/10 and guide CFG creation.


### ITERATION 4: White-Box Testing and Bug Fixes

## Final Report

| Error # | Location | Bug Description | Fix Applied |
|---------|----------|-----------------|-------------|
| 1 | moneypoly/moneypoly/dice.py | Dice roll used 1..5 instead of 1..6, so value 6 was unreachable. | Updated both random calls in roll() to randint(1, 6). |
| 2 | moneypoly/moneypoly/player.py | Passing Go without landing exactly on position 0 did not award Go salary. | Updated move() to detect wrap-around and award salary when passing or landing on Go. |
| 3 | moneypoly/moneypoly/property.py | Full-group ownership check used partial ownership logic, incorrectly enabling rent multiplier. | Replaced any() logic with all() across group properties (with non-empty guard). |
| 4 | moneypoly/moneypoly/game.py | Buying property failed when player balance equaled property price. | Changed affordability condition from <= price to < price. |
| 5 | moneypoly/moneypoly/game.py | Rent was deducted from tenant but not credited to property owner. | Added owner balance credit during pay_rent(). |
| 6 | moneypoly/moneypoly/game.py | Voluntary jail fine collected by bank without deducting player funds. | Added player fine deduction before releasing from jail. |
| 7 | moneypoly/moneypoly/game.py | Winner selection returned minimum net worth player instead of maximum. | Changed winner selection from min() to max() by net worth. |

## Bug-Fix Commits (One Per Error)

- Error #1: 84fa711 - Fixed dice roll range to 1-6
- Error #2: 436456d - Fixed GO salary when passing GO
- Error #3: ece4637 - Fixed full-set ownership check for rent bonus
- Error #4: d6963b3 - Allowed property purchase at exact balance
- Error #5: 11f31ea - Fixed rent transfer to property owner
- Error #6: db2b193 - Deducted voluntary jail fine from player
- Error #7: 9fcff15 - Corrected winner selection to highest net worth

## Verification

- White-box test suite executed successfully: 22 passed, 0 failed.


### ITERATION 5: Strict Modular White-Box Coverage (100% Line + Branch)

## Modular Test Suite Layout

- moneypoly/moneypoly/test/test_bank.py -> moneypoly/moneypoly/bank.py
- moneypoly/moneypoly/test/test_board.py -> moneypoly/moneypoly/board.py
- moneypoly/moneypoly/test/test_cards.py -> moneypoly/moneypoly/cards.py
- moneypoly/moneypoly/test/test_config.py -> moneypoly/moneypoly/config.py
- moneypoly/moneypoly/test/test_dice.py -> moneypoly/moneypoly/dice.py
- moneypoly/moneypoly/test/test_game.py -> moneypoly/moneypoly/game.py
- moneypoly/moneypoly/test/test_player.py -> moneypoly/moneypoly/player.py
- moneypoly/moneypoly/test/test_property.py -> moneypoly/moneypoly/property.py
- moneypoly/moneypoly/test/test_ui.py -> moneypoly/moneypoly/ui.py
- moneypoly/moneypoly/test/test_main.py -> moneypoly/main.py

## Final Coverage Snapshot

Command used:

pytest --cov=main --cov=moneypoly --cov-branch --cov-report=term-missing --cov-fail-under=100 test

Result:

- 189 passed
- 100.00% total coverage
- 100% line coverage and 100% branch coverage for all tracked source modules

Module snapshot:

| Module | Line | Branch |
|--------|------|--------|
| main.py | 100% | 100% |
| moneypoly/bank.py | 100% | 100% |
| moneypoly/board.py | 100% | 100% |
| moneypoly/cards.py | 100% | 100% |
| moneypoly/config.py | 100% | 100% |
| moneypoly/dice.py | 100% | 100% |
| moneypoly/game.py | 100% | 100% |
| moneypoly/player.py | 100% | 100% |
| moneypoly/property.py | 100% | 100% |
| moneypoly/ui.py | 100% | 100% |

## Phase 3 Bug Status For This Strict Run

- No additional source-code defects were discovered during this strict 100% line+branch coverage run.
- Existing previously fixed defects remain resolved under full-coverage execution.
