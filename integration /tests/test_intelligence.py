"""
tests/test_intelligence.py
Unit tests for IntelligenceModule.
"""

import unittest
from tests.helpers import (
    make_modules, register_driver, register_scout, register_strategist
)


class TestIntelligence(unittest.TestCase):

    def setUp(self):
        (self.reg, self.crew, _inv, _race, _res,
         _miss, self.intel, *_) = make_modules()

    # ── Filing reports ────────────────────────────────────────────────────────

    def test_file_report_valid(self):
        scout = register_scout(self.reg, self.crew)
        report = self.intel.file_report(scout.member_id, "DK Crew", "Spotted near docks")
        self.assertEqual(report.rival_crew, "DK Crew")
        self.assertEqual(report.filed_by, scout.member_id)

    def test_file_report_default_threat_unknown(self):
        scout = register_scout(self.reg, self.crew)
        report = self.intel.file_report(scout.member_id, "Shadow Crew", "Info")
        self.assertEqual(report.threat_level, "unknown")

    def test_file_report_creates_rival_profile(self):
        scout = register_scout(self.reg, self.crew)
        self.intel.file_report(scout.member_id, "Ghost Crew", "Details")
        self.assertEqual(self.intel.get_threat_level("Ghost Crew"), "unknown")

    def test_file_multiple_reports_same_rival(self):
        scout = register_scout(self.reg, self.crew)
        self.intel.file_report(scout.member_id, "DK Crew", "Report 1")
        self.intel.file_report(scout.member_id, "DK Crew", "Report 2")
        rival = self.intel._rivals["dk crew"]
        self.assertEqual(len(rival.report_ids), 2)

    # ── Analysing reports ─────────────────────────────────────────────────────

    def test_analyse_report_sets_threat_level(self):
        scout     = register_scout(self.reg, self.crew)
        strat     = register_strategist(self.reg, self.crew)
        report    = self.intel.file_report(scout.member_id, "DK Crew", "Info")
        self.intel.analyse_report(strat.member_id, report.report_id, "high")
        self.assertEqual(report.threat_level, "high")

    def test_analyse_report_sets_analysed_by(self):
        scout  = register_scout(self.reg, self.crew)
        strat  = register_strategist(self.reg, self.crew)
        report = self.intel.file_report(scout.member_id, "DK Crew", "Info")
        self.intel.analyse_report(strat.member_id, report.report_id, "medium")
        self.assertEqual(report.analysed_by, strat.member_id)

    def test_analyse_report_updates_rival_profile(self):
        scout  = register_scout(self.reg, self.crew)
        strat  = register_strategist(self.reg, self.crew)
        report = self.intel.file_report(scout.member_id, "DK Crew", "Info")
        self.intel.analyse_report(strat.member_id, report.report_id, "high")
        self.assertEqual(self.intel.get_threat_level("DK Crew"), "high")

    def test_rival_threat_escalates_only_upward(self):
        scout  = register_scout(self.reg, self.crew)
        strat  = register_strategist(self.reg, self.crew)
        r1 = self.intel.file_report(scout.member_id, "DK Crew", "Report 1")
        r2 = self.intel.file_report(scout.member_id, "DK Crew", "Report 2")
        self.intel.analyse_report(strat.member_id, r1.report_id, "high")
        self.intel.analyse_report(strat.member_id, r2.report_id, "low")
        # Should stay at "high", not be lowered by subsequent "low" analysis
        self.assertEqual(self.intel.get_threat_level("DK Crew"), "high")

    def test_rival_threat_escalates_to_highest(self):
        scout  = register_scout(self.reg, self.crew)
        strat  = register_strategist(self.reg, self.crew)
        r1 = self.intel.file_report(scout.member_id, "DK Crew", "R1")
        r2 = self.intel.file_report(scout.member_id, "DK Crew", "R2")
        self.intel.analyse_report(strat.member_id, r1.report_id, "low")
        self.intel.analyse_report(strat.member_id, r2.report_id, "critical")
        self.assertEqual(self.intel.get_threat_level("DK Crew"), "critical")

    def test_get_threat_level_unknown_rival(self):
        level = self.intel.get_threat_level("No Such Crew")
        self.assertEqual(level, "unknown")

    # ── Error cases ───────────────────────────────────────────────────────────

    def test_file_report_non_scout_raises(self):
        driver = register_driver(self.reg, self.crew)
        with self.assertRaises(ValueError):
            self.intel.file_report(driver.member_id, "Rivals", "Info")

    def test_file_report_unregistered_raises(self):
        with self.assertRaises(ValueError):
            self.intel.file_report("00000000-fake-id", "Rivals", "Info")

    def test_analyse_report_non_strategist_raises(self):
        scout  = register_scout(self.reg, self.crew)
        driver = register_driver(self.reg, self.crew)
        report = self.intel.file_report(scout.member_id, "Rivals", "Info")
        with self.assertRaises(ValueError):
            self.intel.analyse_report(driver.member_id, report.report_id, "high")

    def test_analyse_report_invalid_threat_raises(self):
        scout  = register_scout(self.reg, self.crew)
        strat  = register_strategist(self.reg, self.crew)
        report = self.intel.file_report(scout.member_id, "Rivals", "Info")
        with self.assertRaises(ValueError):
            self.intel.analyse_report(strat.member_id, report.report_id, "extreme")

    def test_analyse_unknown_report_raises(self):
        strat = register_strategist(self.reg, self.crew)
        with self.assertRaises(KeyError):
            self.intel.analyse_report(strat.member_id, "no-such-report", "low")


if __name__ == "__main__":
    unittest.main()
