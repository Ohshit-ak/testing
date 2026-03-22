"""
Module: Crew Management
Responsibility: Manage roles and skill levels for registered crew members.
Depends on: RegistrationModule — a member must be registered first.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from registration import RegistrationModule, CrewMember, VALID_ROLES


SKILL_MIN = 1
SKILL_MAX = 10


@dataclass
class CrewProfile:
    member_id: str
    skill_level: int               # 1 (novice) – 10 (elite)
    specialisations: List[str] = field(default_factory=list)
    race_count: int = 0
    mission_count: int = 0
    is_available: bool = True      # False when busy on a race/mission

    def __str__(self):
        spec = ", ".join(self.specialisations) if self.specialisations else "none"
        avail = "AVAILABLE" if self.is_available else "BUSY"
        return (
            f"  Skill: {self.skill_level}/10 | Specialisations: {spec} | "
            f"Races: {self.race_count} | Missions: {self.mission_count} | {avail}"
        )


class CrewManagementModule:
    """
    Stores and manages crew profiles (skill levels, availability, stats).
    Works alongside RegistrationModule for identity lookups.
    """

    def __init__(self, registration: RegistrationModule):
        self._reg = registration
        self._profiles: Dict[str, CrewProfile] = {}  # member_id -> CrewProfile

    # ------------------------------------------------------------------ #
    #  Profile management                                                  #
    # ------------------------------------------------------------------ #

    def add_profile(self, member_id: str, skill_level: int = 5) -> CrewProfile:
        """Create a crew profile for a registered member."""
        member = self._require_registered(member_id)
        if member_id in self._profiles:
            raise ValueError(f"Profile for '{member.name}' already exists.")
        if not (SKILL_MIN <= skill_level <= SKILL_MAX):
            raise ValueError(f"Skill level must be between {SKILL_MIN} and {SKILL_MAX}.")

        profile = CrewProfile(member_id=member_id, skill_level=skill_level)
        self._profiles[member_id] = profile
        print(f"[CREW] Profile created for {member.name} (skill {skill_level}/10).")
        return profile

    def update_skill(self, member_id: str, new_skill: int) -> None:
        member = self._require_registered(member_id)
        profile = self._get_profile_or_raise(member_id)
        if not (SKILL_MIN <= new_skill <= SKILL_MAX):
            raise ValueError(f"Skill level must be {SKILL_MIN}–{SKILL_MAX}.")
        profile.skill_level = new_skill
        print(f"[CREW] {member.name}'s skill updated to {new_skill}/10.")

    def add_specialisation(self, member_id: str, spec: str) -> None:
        member = self._require_registered(member_id)
        profile = self._get_profile_or_raise(member_id)
        spec = spec.strip().lower()
        if spec not in profile.specialisations:
            profile.specialisations.append(spec)
            print(f"[CREW] '{spec}' added to {member.name}'s specialisations.")

    # ------------------------------------------------------------------ #
    #  Availability                                                        #
    # ------------------------------------------------------------------ #

    def set_availability(self, member_id: str, available: bool) -> None:
        self._get_profile_or_raise(member_id)
        self._profiles[member_id].is_available = available

    def is_available(self, member_id: str) -> bool:
        profile = self._profiles.get(member_id)
        return profile.is_available if profile else False

    def get_available_by_role(self, role: str) -> List[CrewMember]:
        """Return registered active members with the given role who are available."""
        members = self._reg.get_members_by_role(role)
        return [
            m for m in members
            if self._profiles.get(m.member_id) and
               self._profiles[m.member_id].is_available
        ]

    # ------------------------------------------------------------------ #
    #  Stats (called by Race/Mission modules)                              #
    # ------------------------------------------------------------------ #

    def record_race(self, member_id: str) -> None:
        self._get_profile_or_raise(member_id).race_count += 1

    def record_mission(self, member_id: str) -> None:
        self._get_profile_or_raise(member_id).mission_count += 1

    # ------------------------------------------------------------------ #
    #  Queries                                                             #
    # ------------------------------------------------------------------ #

    def get_profile(self, member_id: str) -> Optional[CrewProfile]:
        return self._profiles.get(member_id)

    def list_crew(self) -> None:
        print("\n=== CREW PROFILES ===")
        members = self._reg.get_active_members()
        if not members:
            print("  (no active members)")
        for member in members:
            profile = self._profiles.get(member.member_id)
            print(f"  {member}")
            if profile:
                print(profile)
            else:
                print("  (no profile yet)")
        print()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _require_registered(self, member_id: str) -> CrewMember:
        member = self._reg.get_member(member_id)
        if member is None or not member.is_active:
            raise ValueError(
                f"Member '{member_id}' is not registered / active. "
                "Register them first via RegistrationModule."
            )
        return member

    def _get_profile_or_raise(self, member_id: str) -> CrewProfile:
        profile = self._profiles.get(member_id)
        if profile is None:
            raise KeyError(
                f"No crew profile for member '{member_id}'. "
                "Call add_profile() first."
            )
        return profile
