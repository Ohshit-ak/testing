# MoneyPoly Control Flow Graph (CFG) — Hand-Drawing Guide

Use this checklist to produce a clear, hand-drawn CFG for the MoneyPoly game. Focus on control flow (decisions, loops, calls), not data details.

## What to include
- Entry: `main()` → `get_player_names()` → `Game(names)` → `Game.run()`.
- Main loop: `run()` while-condition and loop back-edge.
- Per-turn path: `play_turn`, `_move_and_resolve`, `_handle_property_tile`, `_handle_jail_turn`, `_apply_card`, `_check_bankruptcy`, `find_winner`.
- Skip UI-only print helpers; keep decisions and loops that change flow.

## Notation (keep it simple)
- **Rectangle**: statement/block (e.g., “roll dice”, “advance_turn”).
- **Diamond**: decision/branch (e.g., “player.in_jail?”).
- **Circle / small connector**: join points or off-page connectors if needed.
- **Arrows**: label outcomes (True/False, or specific choices like b/a/s).

## Step-by-step drawing
1) **Entry chain**
   - Node: `main()`
   - Arrow to: `get_player_names()`
   - Arrow to: `Game(names)` (ctor)
   - Arrow to: `run()` (entry to loop)

2) **Game loop in `run()`**
   - Diamond: condition `running and turn_number < MAX_TURNS and len(players) > 1`
     - True → arrow to `play_turn`
     - False → arrow to `find_winner` → `print result` → **End**
   - From `play_turn` return, draw back-edge to loop condition.

3) **Turn flow in `play_turn`**
   - Rectangle: “banner/current_player”
   - Diamond: `player.in_jail?`
     - Yes → `_handle_jail_turn` → `advance_turn` → **Return to loop**
     - No → continue
   - Rectangle: `roll = dice.roll()`
   - Diamond: `doubles_streak >= 3?`
     - Yes → `player.go_to_jail` → `advance_turn` → **Return**
     - No → continue
   - Rectangle: `_move_and_resolve(player, roll)`
   - Diamond: `dice.is_doubles?`
     - Yes → **Return** (extra turn, no advance)
     - No → `advance_turn` → **Return**

4) **Movement resolution in `_move_and_resolve`**
   - Rectangle: `player.move(steps)` → `tile = board.get_tile_type(pos)`
   - Multi-branch diamond on `tile`:
     - `go_to_jail` → `player.go_to_jail`
     - `income_tax` → `deduct`, `bank.collect`
     - `luxury_tax` → similar
     - `free_parking` → no-op
     - `chance` → `card = chance_deck.draw` → `_apply_card`
     - `community_chest` → draw → `_apply_card`
     - `railroad` or `property` → `_handle_property_tile`
     - `blank` → no-op
   - Join arrows back to rectangle: `_check_bankruptcy(player)`
   - Arrow back to caller (`play_turn`)

5) **Property handling in `_handle_property_tile`**
   - Diamond: `prop.owner is None?`
     - Yes → choice (input) diamond: `b/a/s` (buy/auction/skip)
       - b → `buy_property`
       - a → `auction_property`
       - s → pass
     - No → diamond: `owner == player?`
       - Yes → “no rent” (return)
       - No → `pay_rent`
   - Return to caller

6) **Card effects in `_apply_card`**
   - Diamond on `action` value:
     - `collect` → `bank.pay_out` → `player.add_money`
     - `pay` → `player.deduct_money` → `bank.collect`
     - `jail` → `player.go_to_jail`
     - `jail_free` → increment card count
     - `move_to` → set position, maybe `+GO_SALARY`, maybe `_handle_property_tile`
     - `birthday` → loop over others: `deduct`, `player.add`
     - `collect_from_all` → similar loop
   - Return to caller

7) **Jail turn in `_handle_jail_turn`**
   - Diamond: `has get_out_of_jail_card?`
     - Yes → prompt → if use: exit jail → roll → `_move_and_resolve` → return
   - Diamond: `pay fine?`
     - Yes → pay → roll → `_move_and_resolve` → return
   - Else: `jail_turns += 1`
     - Diamond: `jail_turns >= 3?`
       - Yes → mandatory pay → roll → `_move_and_resolve`
       - No → return

8) **Bankruptcy check `_check_bankruptcy`**
   - Diamond: `player.is_bankrupt?`
     - Yes → eliminate player (remove, release props, fix index)
     - No → return

9) **End of game**
   - From loop false branch: `find_winner` → banner/print → **End**

## Visual layout tips
- Keep vertical flow top-to-bottom; align branch joins before returning to callers.
- Label edges clearly (True/False, b/a/s, tile names).
- Use small connector circles if arrows would cross too much.
- Leave space between major blocks (`run`, `play_turn`, `_move_and_resolve`) so it stays readable.

## Sanity check before finishing
- Every decision in code has a diamond and both outcomes drawn.
- Loops have a back-edge: `run` loop, dice doubles extra-turn implicit return, jail 3-turn logic.
- Calls that can branch internally (`_move_and_resolve`, `_apply_card`, `_handle_jail_turn`) have their branch structure represented.
- Entry and exit are clear: one Start, one End.
