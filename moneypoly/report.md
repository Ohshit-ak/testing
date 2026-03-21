
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
    


## Notes
- No gameplay logic changed; only lint suppressions and documentation were added to achieve pylint 10/10 and guide CFG creation.
