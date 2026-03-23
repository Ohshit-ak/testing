"""
Module: Intelligence (Extra Module 1)
Responsibility: Track rival crews, gather intel reports, and assess threat levels.
Scouts can generate intel; strategists can analyse it.
Depends on: CrewManagementModule, RegistrationModule.

Design rationale: In underground racing, knowledge of rival crews is critical.
This module lets scouts file intel reports on rivals and strategists convert
raw reports into actionable threat assessments that feed into Race and Mission
decisions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid
from datetime import datetime

from registration import RegistrationModule
from crew_management import CrewManagementModule


THREAT_LEVELS = ("unknown", "low", "medium", "high", "critical")


@dataclass
class IntelReport:
    report_id: str
    filed_by: str              # member_id of scout
    rival_crew: str
    details: str
    threat_level: str = "unknown"
    analysed_by: Optional[str] = None  # member_id of strategist
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    def __str__(self):
        analyst = f" | Analysed by: {self.analysed_by[:8] if self.analysed_by else 'N/A'}"
        return (
            f"[{self.report_id[:8]}] Rival: '{self.rival_crew}' | "
            f"Threat: {self.threat_level.upper()} | Filed: {self.timestamp}{analyst}"
        )


@dataclass
class RivalProfile:
    rival_name: str
    threat_level: str = "unknown"
    report_ids: List[str] = field(default_factory=list)

    def __str__(self):
        return f"{self.rival_name} | Overall threat: {self.threat_level.upper()} | Reports: {len(self.report_ids)}"


class IntelligenceModule:
    """
    Manages intelligence gathering on rival crews.
    - Scouts file raw intel reports.
    - Strategists analyse reports and set/upgrade threat levels.
    - Rival profiles are maintained for quick threat overview.
    """

    def __init__(self, registration: RegistrationModule, crew: CrewManagementModule):
        self._reg = registration
        self._crew = crew
        self._reports: Dict[str, IntelReport] = {}
        self._rivals: Dict[str, RivalProfile] = {}   # rival_name (lower) -> RivalProfile

    # ------------------------------------------------------------------ #
    #  Intel filing                                                        #
    # ------------------------------------------------------------------ #

    def file_report(self, scout_id: str, rival_crew: str, details: str) -> IntelReport:
        """A scout files a raw intel report on a rival crew."""
        member = self._reg.get_member(scout_id)
        if member is None or not member.is_active:
            raise ValueError(f"Scout '{scout_id}' is not registered / active.")
        if member.role != "scout":
            raise ValueError(
                f"Only scouts can file intel reports ('{member.name}' is a '{member.role}')."
            )

        rival_crew = rival_crew.strip()
        report = IntelReport(
            report_id=str(uuid.uuid4()),
            filed_by=scout_id,
            rival_crew=rival_crew,
            details=details,
        )
        self._reports[report.report_id] = report

        # Create or update rival profile
        key = rival_crew.lower()
        if key not in self._rivals:
            self._rivals[key] = RivalProfile(rival_name=rival_crew)
        self._rivals[key].report_ids.append(report.report_id)

        print(f"[INTEL] 📋 Report filed by {member.name} on '{rival_crew}'.")
        return report

    def analyse_report(
        self, strategist_id: str, report_id: str, threat_level: str
    ) -> None:
        """A strategist analyses a report and assigns a threat level."""
        member = self._reg.get_member(strategist_id)
        if member is None or not member.is_active:
            raise ValueError(f"Strategist '{strategist_id}' is not registered / active.")
        if member.role != "strategist":
            raise ValueError(
                f"Only strategists can analyse reports ('{member.name}' is a '{member.role}')."
            )

        threat_level = threat_level.lower()
        if threat_level not in THREAT_LEVELS:
            raise ValueError(f"Threat level must be one of: {THREAT_LEVELS}.")

        report = self._reports.get(report_id)
        if report is None:
            raise KeyError(f"Report '{report_id}' not found.")

        report.threat_level = threat_level
        report.analysed_by = strategist_id

        # Escalate rival profile threat to highest known level
        rival_key = report.rival_crew.lower()
        rival = self._rivals.get(rival_key)
        if rival:
            current_idx = THREAT_LEVELS.index(rival.threat_level)
            new_idx = THREAT_LEVELS.index(threat_level)
            if new_idx > current_idx:
                rival.threat_level = threat_level

        print(
            f"[INTEL] 🔍 {member.name} assessed '{report.rival_crew}' "
            f"as {threat_level.upper()} threat."
        )

    # ------------------------------------------------------------------ #
    #  Display                                                             #
    # ------------------------------------------------------------------ #

    def show_rivals(self) -> None:
        print("\n=== RIVAL CREWS ===")
        if not self._rivals:
            print("  (no rival data gathered yet)")
        for rp in self._rivals.values():
            print(f"  {rp}")
        print()

    def show_reports(self, rival_crew: Optional[str] = None) -> None:
        print("\n=== INTEL REPORTS ===")
        reports = self._reports.values()
        if rival_crew:
            reports = [r for r in reports if r.rival_crew.lower() == rival_crew.lower()]
        if not reports:
            print("  (no reports)")
        for r in reports:
            print(f"  {r}")
            print(f"    Details: {r.details}")
        print()

    def get_threat_level(self, rival_crew: str) -> str:
        rival = self._rivals.get(rival_crew.lower())
        return rival.threat_level if rival else "unknown"
