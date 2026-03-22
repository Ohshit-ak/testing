# MoneyPoly Bug-Fix and Refactor Assignment Report

Prepared for assignment submission.

---

## 1. Executive Summary

This report documents a full white-box audit, targeted defect correction, and lint-compliant refactor for the MoneyPoly codebase.

Final state:
- 11 functional bugs fixed in sequence.
- Strict test suite passing: 193/193.
- Coverage maintained at 100% line and 100% branch.
- Pylint result on innermost package: 10.00/10.
- No inline suppression comments used for final compliance.
- Relaxed pylint config removed from repository.

---

## 2. Scope and Codebase

Source package under test:
- moneypoly/moneypoly/moneypoly/

Primary modules:
- bank.py
- board.py
- cards.py
- config.py
- dice.py
- game.py
- player.py
- property.py
- ui.py
- __init__.py

Test suite location:
- moneypoly/moneypoly/test/

---

## 3. Verification Method

### 3.1 White-Box Test Strategy

The suite was executed with branch-aware tests for control-flow paths, edge cases, and state transitions.

Areas covered:
- dice range and doubles handling
- player movement and GO salary logic
- property ownership and rent behavior
- tax, jail, and card action branches
- trade, mortgage, and loan money flow
- winner selection and elimination behavior

### 3.2 Commands Used

Lint:
- python -m pylint moneypoly/moneypoly/moneypoly

Tests:
- python -m pytest -q

Coverage:
- python -m pytest --cov=main --cov=moneypoly --cov-branch --cov-report=term-missing --cov-fail-under=100 test

### 3.3 Final Verification Snapshot

- pytest: 193 passed
- pylint: 10.00/10
- coverage: 100.00% total (line and branch)

---

## 4. Bug Resolution Summary (11/11)

| Bug # | Module | Method | Issue | Commit |
|------:|--------|--------|-------|--------|
| 1 | game.py | mortgage_property() | Removed inverse bank collection path during mortgage payout flow | e7710a0 |
| 2 | game.py | trade() | Added missing seller credit in cash transfer | e3c8dcc |
| 3 | game.py | _apply_card() | Corrected move_to pass-GO condition | 2c78dd2 |
| 4 | game.py | _apply_card() | Applied partial collection logic for birthday / collect_from_all | 865d08f |
| 5 | player.py | net_worth() | Included unmortgaged property value in net worth | e98b453 |
| 6 | player.py | move() | Fixed GO salary edge case around position 0 transition | bfd6b73 |
| 7 | board.py | is_purchasable() | Replaced fragile identity check with truthy check | 69335fc |
| 8 | bank.py | give_loan() | Deducted reserves when issuing loan | c2c283d |
| 9 | cards.py | CardDeck.reshuffle() | Added empty-deck guard before reshuffle | a85c600 |
| 10 | dice.py | Dice.__init__() | Removed redundant constructor initialization sequence | 07bca71 |
| 11 | ui.py | print_player_card() | Printed jail line only when non-empty | 97e89ae |

---

## 5. Refactor and Compliance Summary

### 5.1 Why Refactor Was Required

Default pylint thresholds were initially bypassed by configuration tuning. This was replaced with code-level refactors to satisfy default rules legitimately.

### 5.2 Final Compliance Actions

- Added package metadata and missing module docs where needed.
- Removed inline suppression style from source.
- Reworked game/player/property internals using composition and helper extraction.
- Removed relaxed .pylintrc from repository.
- Cleaned tracked bytecode cache artifacts from git history moving forward.

---

## 6. Commit-by-Commit Audit Trail

The format below is intentionally uniform for assignment review and grading.

## Commit 1 — Stop inverse bank collect on mortgage payout

| Field | Detail |
|------|--------|
| Commit | e7710a0 |
| File | moneypoly/moneypoly/moneypoly/game.py |
| Method | mortgage_property() |
| Type | Bug Fix |
| Severity | Medium |
| Pylint delta | no change |
| Lines changed | 21 |

Root cause / motivation:
Mortgage payout path included inverse bank flow logic and produced invalid reserve behavior.

What was changed:
The problematic inverse-collection behavior was removed from the mortgage payout path.

---

## Commit 2 — Credit seller during trade cash transfer

| Field | Detail |
|------|--------|
| Commit | e3c8dcc |
| File | moneypoly/moneypoly/moneypoly/game.py |
| Method | trade() |
| Type | Bug Fix |
| Severity | Critical |
| Pylint delta | no change |
| Lines changed | 20 |

Root cause / motivation:
Trade deducted buyer cash but did not credit seller, causing money loss.

What was changed:
Seller credit was added directly after buyer deduction.

---

## Commit 3 — Correct pass-GO check for move_to cards

| Field | Detail |
|------|--------|
| Commit | 2c78dd2 |
| File | moneypoly/moneypoly/moneypoly/game.py |
| Method | _apply_card() |
| Type | Bug Fix |
| Severity | Medium |
| Pylint delta | no change |
| Lines changed | 21 |

Root cause / motivation:
GO salary condition missed boundary behavior in move_to transitions.

What was changed:
Pass-GO logic in the move_to branch was corrected for edge transitions.

---

## Commit 4 — Collect partial card payments from all players

| Field | Detail |
|------|--------|
| Commit | 865d08f |
| File | moneypoly/moneypoly/moneypoly/game.py |
| Method | _apply_card() |
| Type | Bug Fix |
| Severity | Medium |
| Pylint delta | no change |
| Lines changed | 45 |

Root cause / motivation:
Players below full payment threshold were skipped instead of paying available balance.

What was changed:
Both birthday and collect_from_all flows now use partial payment semantics.

---

## Commit 5 — Include property value in net worth

| Field | Detail |
|------|--------|
| Commit | e98b453 |
| File | moneypoly/moneypoly/moneypoly/player.py |
| Method | net_worth() |
| Type | Bug Fix |
| Severity | Medium |
| Pylint delta | no change |
| Lines changed | 32 |

Root cause / motivation:
Net worth excluded owned properties and produced incorrect standings.

What was changed:
Unmortgaged property mortgage-values were included in net worth calculation.

---

## Commit 6 — Correct pass-GO edge condition in move

| Field | Detail |
|------|--------|
| Commit | bfd6b73 |
| File | moneypoly/moneypoly/moneypoly/player.py |
| Method | move() |
| Type | Bug Fix |
| Severity | Medium |
| Pylint delta | no change |
| Lines changed | 33 |

Root cause / motivation:
GO salary condition could reward incorrectly at position-0 edge case.

What was changed:
Pass-GO check was updated to use explicit wrap-aware condition.

---

## Commit 7 — Simplify mortgaged check in purchasable logic

| Field | Detail |
|------|--------|
| Commit | 69335fc |
| File | moneypoly/moneypoly/moneypoly/board.py |
| Method | is_purchasable() |
| Type | Bug Fix |
| Severity | Low |
| Pylint delta | no change |
| Lines changed | 21 |

Root cause / motivation:
Identity check pattern was brittle and non-idiomatic.

What was changed:
Mortgaged condition now uses direct truthiness.

---

## Commit 8 — Deduct reserves when issuing loans

| Field | Detail |
|------|--------|
| Commit | c2c283d |
| File | moneypoly/moneypoly/moneypoly/bank.py |
| Method | give_loan() |
| Type | Bug Fix |
| Severity | Medium |
| Pylint delta | no change |
| Lines changed | 27 |

Root cause / motivation:
Loan issuance credited player balances without reducing bank reserves.

What was changed:
Reserve deduction was added to keep bank accounting consistent.

---

## Commit 9 — Guard reshuffle on empty decks

| Field | Detail |
|------|--------|
| Commit | a85c600 |
| File | moneypoly/moneypoly/moneypoly/cards.py |
| Method | CardDeck.reshuffle() |
| Type | Bug Fix |
| Severity | Low |
| Pylint delta | no change |
| Lines changed | 28 |

Root cause / motivation:
Reshuffle lacked parity with empty-deck protections present in other deck methods.

What was changed:
Early-return guard was added for empty deck input.

---

## Commit 10 — Remove redundant Dice constructor assignments

| Field | Detail |
|------|--------|
| Commit | 07bca71 |
| File | moneypoly/moneypoly/moneypoly/dice.py |
| Method | __init__() |
| Type | Bug Fix |
| Severity | Low |
| Pylint delta | no change |
| Lines changed | 25 |

Root cause / motivation:
Constructor state assignments were immediately overwritten by reset().

What was changed:
Initialization sequence was simplified to remove redundancy.

---

## Commit 11 — Print jail line only when relevant

| Field | Detail |
|------|--------|
| Commit | 97e89ae |
| File | moneypoly/moneypoly/moneypoly/ui.py |
| Method | print_player_card() |
| Type | Bug Fix |
| Severity | Low |
| Pylint delta | no change |
| Lines changed | 22 |

Root cause / motivation:
Non-jailed path made unconditional empty print calls.

What was changed:
Jail line output now executes only when content exists.

---

## Commit 12 — Add package metadata and missing module docs

| Field | Detail |
|------|--------|
| Commit | 3325110 |
| File | moneypoly/moneypoly/moneypoly/__init__.py, moneypoly/moneypoly/moneypoly/config.py |
| Method | N/A |
| Type | Refactor |
| Severity | N/A |
| Pylint delta | improved |
| Lines changed | 22 |

Root cause / motivation:
Package/doc metadata gaps weakened static-analysis quality.

What was changed:
Package initializer and module documentation were added.

---

## Commit 13 — Intermediate suppression cleanup pass

| Field | Detail |
|------|--------|
| Commit | 0abb261 |
| File | game.py, player.py, property.py, .pylintrc |
| Method | N/A |
| Type | Refactor |
| Severity | N/A |
| Pylint delta | improved |
| Lines changed | 42 |

Root cause / motivation:
Initial cleanup removed inline suppressions but still depended on config tuning.

What was changed:
Inline comment suppressions were removed in preparation for final code-only compliance.

---

## Commit 14 — Code-only refactor for default pylint 10.00

| Field | Detail |
|------|--------|
| Commit | a28f98d |
| File | game.py, player.py, property.py |
| Method | _apply_card(), __init__(), state composition helpers |
| Type | Refactor |
| Severity | N/A |
| Pylint delta | 9.91 -> 10.00 |
| Lines changed | 343 |

Root cause / motivation:
Default pylint thresholds required structural improvements without suppression or relaxed settings.

What was changed:
Composed state objects and helper extraction were introduced; final lint compliance achieved under default thresholds.

---

## Commit 15 — Stop tracking generated bytecode caches

| Field | Detail |
|------|--------|
| Commit | a44303e |
| File | __pycache__ artifacts (tracked removals) |
| Method | N/A |
| Type | Refactor |
| Severity | Low |
| Pylint delta | no change |
| Lines changed | binary/cache removals only |

Root cause / motivation:
Tracked generated caches caused recurring dirty repository state.

What was changed:
Tracked cache artifacts were removed from version control.

---

## Commit 16 — Final documentation update for cleanup entry

| Field | Detail |
|------|--------|
| Commit | 2df9d47 |
| File | moneypoly/report.md |
| Method | N/A |
| Type | Documentation |
| Severity | N/A |
| Pylint delta | no change |
| Lines changed | 19 |

Root cause / motivation:
Audit trail needed explicit documentation of repository cleanup commit.

What was changed:
A dedicated report entry was added for the cache cleanup change.

---

## 7. Final Compliance Checklist

- [x] All 11 requested bugs fixed in sequence.
- [x] One focused commit per functional bug fix.
- [x] Final pylint score is exactly 10.00/10 on innermost package.
- [x] No inline pylint disable comments in final source.
- [x] No relaxed pylint thresholds retained in repository config.
- [x] Report contains normalized, reviewer-friendly commit traceability.
- [x] Test suite passes in final state (193/193).
- [x] Coverage target maintained at 100% line and branch.

---

## 8. Submission Note

This version replaces iterative notes with an assignment-style technical document intended for evaluator review.
