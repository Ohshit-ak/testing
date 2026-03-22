"""
Module: Registration
Responsibility: Register new crew members with name and role.
All other modules depend on registration — a member must exist here
before any other module can interact with them.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import uuid


VALID_ROLES = {"driver", "mechanic", "strategist", "scout", "medic"}


@dataclass
class CrewMember:
    member_id: str
    name: str
    role: str
    is_active: bool = True

    def __str__(self):
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"[{self.member_id[:8]}] {self.name} | Role: {self.role.upper()} | {status}"


class RegistrationModule:
    """
    Handles registration of new crew members.
    Acts as the authoritative source for member identity.
    """

    def __init__(self):
        self._members: Dict[str, CrewMember] = {}  # member_id -> CrewMember

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def register(self, name: str, role: str) -> CrewMember:
        """Register a new crew member. Returns the created CrewMember."""
        name = name.strip()
        role = role.strip().lower()

        if not name:
            raise ValueError("Name cannot be empty.")
        if role not in VALID_ROLES:
            raise ValueError(
                f"Invalid role '{role}'. Valid roles: {', '.join(sorted(VALID_ROLES))}"
            )
        if self._name_exists(name):
            raise ValueError(f"A crew member named '{name}' is already registered.")

        member = CrewMember(
            member_id=str(uuid.uuid4()),
            name=name,
            role=role,
        )
        self._members[member.member_id] = member
        print(f"[REGISTRATION] ✓ Registered: {member}")
        return member

    def deactivate(self, member_id: str) -> None:
        """Mark a crew member as inactive (soft delete)."""
        member = self._get_or_raise(member_id)
        member.is_active = False
        print(f"[REGISTRATION] Member '{member.name}' deactivated.")

    def get_member(self, member_id: str) -> Optional[CrewMember]:
        return self._members.get(member_id)

    def get_active_members(self) -> list[CrewMember]:
        return [m for m in self._members.values() if m.is_active]

    def get_members_by_role(self, role: str) -> list[CrewMember]:
        role = role.lower()
        return [m for m in self._members.values() if m.role == role and m.is_active]

    def list_all(self) -> None:
        print("\n=== REGISTERED CREW ===")
        if not self._members:
            print("  (no members registered)")
        for m in self._members.values():
            print(f"  {m}")
        print()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get_or_raise(self, member_id: str) -> CrewMember:
        member = self._members.get(member_id)
        if member is None:
            raise KeyError(f"No crew member with ID '{member_id}'.")
        return member

    def _name_exists(self, name: str) -> bool:
        return any(m.name.lower() == name.lower() for m in self._members.values())
