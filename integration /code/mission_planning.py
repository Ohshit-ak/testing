"""
Module: Mission Planning
Responsibility: Assign missions, verify required roles are available,
                track mission outcomes, handle costs.
Depends on: RegistrationModule, CrewManagementModule, InventoryModule.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid

from registration import RegistrationModule
from crew_management import CrewManagementModule
from inventory import InventoryModule

MISSION_TYPES = {
    "delivery":   {"required_roles": ["driver"],              "cost": 500,  "reward": 1500},
    "rescue":     {"required_roles": ["driver", "medic"],     "cost": 800,  "reward": 3000},
    "repair_run": {"required_roles": ["mechanic"],            "cost": 300,  "reward": 900},
    "recon":      {"required_roles": ["scout"],               "cost": 200,  "reward": 700},
    "extraction": {"required_roles": ["driver", "strategist"],"cost": 1000, "reward": 4000},
}


@dataclass
class Mission:
    mission_id: str
    mission_type: str
    description: str
    assigned_members: List[str]   # member_ids
    cost: float
    reward: float
    status: str = "PENDING"       # PENDING | IN_PROGRESS | COMPLETED | FAILED

    def __str__(self):
        members_count = len(self.assigned_members)
        return (
            f"[{self.mission_id[:8]}] {self.mission_type.upper()} | "
            f"'{self.description}' | Members: {members_count} | "
            f"Cost: ${self.cost:,.2f} | Reward: ${self.reward:,.2f} | {self.status}"
        )


class MissionPlanningModule:
    """
    Plans and executes missions.
    Enforces:
      - Required roles must be available before a mission starts.
      - If a mission requires a mechanic (e.g. repair_run) and a car is damaged,
        mechanic availability is checked first.
      - Costs are debited from inventory; rewards credited on completion.
    """

    def __init__(
        self,
        registration: RegistrationModule,
        crew: CrewManagementModule,
        inventory: InventoryModule,
    ):
        self._reg = registration
        self._crew = crew
        self._inv = inventory
        self._missions: Dict[str, Mission] = {}

    # ------------------------------------------------------------------ #
    #  Mission lifecycle                                                   #
    # ------------------------------------------------------------------ #

    def plan_mission(
        self,
        mission_type: str,
        description: str,
        custom_cost: Optional[float] = None,
        custom_reward: Optional[float] = None,
    ) -> Mission:
        """
        Plan a mission. Verifies required roles exist in the active roster,
        then creates the mission in PENDING state (does not commit crew yet).
        """
        mission_type = mission_type.lower()
        if mission_type not in MISSION_TYPES:
            raise ValueError(
                f"Unknown mission type '{mission_type}'. "
                f"Valid types: {', '.join(MISSION_TYPES)}"
            )

        config = MISSION_TYPES[mission_type]
        required_roles = config["required_roles"]
        cost = custom_cost if custom_cost is not None else config["cost"]
        reward = custom_reward if custom_reward is not None else config["reward"]

        # Verify at least one available member per required role
        for role in required_roles:
            available = self._crew.get_available_by_role(role)
            if not available:
                raise ValueError(
                    f"Mission CANNOT start: no available '{role}' found. "
                    f"Required roles: {required_roles}."
                )

        mission = Mission(
            mission_id=str(uuid.uuid4()),
            mission_type=mission_type,
            description=description,
            assigned_members=[],
            cost=cost,
            reward=reward,
        )
        self._missions[mission.mission_id] = mission
        print(f"[MISSION] Planned: {mission}")
        return mission

    def assign_member(self, mission_id: str, member_id: str) -> None:
        """Assign a crew member to a PENDING mission."""
        mission = self._get_mission_or_raise(mission_id)
        if mission.status != "PENDING":
            raise ValueError(f"Cannot assign to a mission with status '{mission.status}'.")

        member = self._reg.get_member(member_id)
        if member is None or not member.is_active:
            raise ValueError(f"Member '{member_id}' is not registered / active.")
        if not self._crew.is_available(member_id):
            raise ValueError(f"'{member.name}' is not available.")

        config = MISSION_TYPES[mission.mission_type]
        if member.role not in config["required_roles"]:
            raise ValueError(
                f"'{member.name}' has role '{member.role}', but this mission "
                f"needs: {config['required_roles']}."
            )

        mission.assigned_members.append(member_id)
        self._crew.set_availability(member_id, False)
        print(f"[MISSION] {member.name} ({member.role}) assigned to '{mission.description}'.")

    def start_mission(self, mission_id: str) -> None:
        """Start a mission — deducts cost, verifies all required roles covered."""
        mission = self._get_mission_or_raise(mission_id)
        if mission.status != "PENDING":
            raise ValueError(f"Mission is not PENDING (status: {mission.status}).")

        config = MISSION_TYPES[mission.mission_type]
        required_roles = set(config["required_roles"])
        assigned_roles = set()
        for mid in mission.assigned_members:
            m = self._reg.get_member(mid)
            if m:
                assigned_roles.add(m.role)

        missing = required_roles - assigned_roles
        if missing:
            raise ValueError(
                f"Cannot start mission — missing roles: {missing}. Assign them first."
            )

        self._inv.debit(mission.cost, reason=f"Mission cost: {mission.description}")
        mission.status = "IN_PROGRESS"
        print(f"[MISSION] 🚀 Mission '{mission.description}' is IN PROGRESS.")

    def complete_mission(self, mission_id: str, success: bool = True) -> None:
        """
        Finalise a mission.
        On success: credit reward, record mission for each member.
        On failure: no reward, members still freed.
        """
        mission = self._get_mission_or_raise(mission_id)
        if mission.status != "IN_PROGRESS":
            raise ValueError(f"Mission is not IN_PROGRESS (status: {mission.status}).")

        if success:
            self._inv.credit(mission.reward, reason=f"Mission reward: {mission.description}")
            mission.status = "COMPLETED"
            print(f"[MISSION] ✅ Mission '{mission.description}' COMPLETED.")
        else:
            mission.status = "FAILED"
            print(f"[MISSION] ❌ Mission '{mission.description}' FAILED. No reward.")

        for mid in mission.assigned_members:
            self._crew.set_availability(mid, True)
            self._crew.record_mission(mid)

    def abort_mission(self, mission_id: str) -> None:
        """Abort a PENDING mission (before it started — no cost charged)."""
        mission = self._get_mission_or_raise(mission_id)
        if mission.status not in ("PENDING",):
            raise ValueError(f"Cannot abort mission in status '{mission.status}'.")
        mission.status = "FAILED"
        for mid in mission.assigned_members:
            self._crew.set_availability(mid, True)
        print(f"[MISSION] Mission '{mission.description}' aborted.")

    # ------------------------------------------------------------------ #
    #  Display                                                             #
    # ------------------------------------------------------------------ #

    def list_missions(self) -> None:
        print("\n=== MISSIONS ===")
        if not self._missions:
            print("  (no missions planned)")
        for m in self._missions.values():
            print(f"  {m}")
        print()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get_mission_or_raise(self, mission_id: str) -> Mission:
        m = self._missions.get(mission_id)
        if m is None:
            raise KeyError(f"Mission '{mission_id}' not found.")
        return m
