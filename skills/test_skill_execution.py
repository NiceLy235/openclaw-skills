#!/usr/bin/env python3
"""
Skill Execution Flow Test Script

Tests whether OpenClaw skills strictly follow step-by-step execution rules.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import json

class SkillTester:
    """Test skill execution flow structure"""

    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.results = {}

    def test_skill(self, skill_name: str) -> Dict:
        """Test a single skill for execution flow compliance"""
        skill_dir = self.skills_dir / skill_name
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.exists():
            return {
                "name": skill_name,
                "status": "error",
                "message": "SKILL.md not found"
            }

        content = skill_file.read_text()

        result = {
            "name": skill_name,
            "status": "success",
            "checks": {}
        }

        # Check 1: Has MANDATORY/CRITICAL rules section
        mandatory_patterns = [
            r'(MANDATORY|CRITICAL).*[Rr]ules?',
            r'(MANDATORY|CRITICAL).*[Ee]xecution',
            r'(MANDATORY|CRITICAL).*[Rr]equirements?'
        ]
        result["checks"]["has_mandatory_rules"] = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in mandatory_patterns
        )

        # Check 2: Has step-by-step structure
        step_patterns = [
            r'Step\s+\d+:',
            r'步骤\s*\d+',
            r'###\s*Step\s+\d+',
            r'###\s*步骤'
        ]
        result["checks"]["has_step_structure"] = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in step_patterns
        )

        # Check 3: Has execution template or workflow
        template_patterns = [
            r'[Ee]xecution\s+[Tt]emplate',
            r'[Ww]orkflow',
            r'执行模板',
            r'执行流程'
        ]
        result["checks"]["has_execution_template"] = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in template_patterns
        )

        # Check 4: Requires user confirmation
        confirmation_patterns = [
            r'confirm|confirmation',
            r'确认|等待.*确认',
            r'Wait for user',
            r'user.*confirm'
        ]
        result["checks"]["requires_confirmation"] = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in confirmation_patterns
        )

        # Check 5: Progress reporting rules
        progress_patterns = [
            r'[Pp]rogress.*report',
            r'进度.*报告',
            r'[Rr]eport.*progress',
            r'reporting.*step',
            r'每.*步.*报告'
        ]
        result["checks"]["has_progress_rules"] = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in progress_patterns
        )

        # Check 6: Stop on error rule
        error_patterns = [
            r'stop on error',
            r'停止.*错误',
            r'fail.*stop',
            r'error.*stop'
        ]
        result["checks"]["has_stop_on_error"] = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in error_patterns
        )

        # Overall compliance score
        passed_checks = sum(result["checks"].values())
        total_checks = len(result["checks"])
        result["compliance_score"] = f"{passed_checks}/{total_checks}"
        result["compliance_percent"] = round(passed_checks / total_checks * 100, 1)

        # Determine overall status
        if result["compliance_percent"] >= 80:
            result["overall_status"] = "PASS"
        elif result["compliance_percent"] >= 60:
            result["overall_status"] = "WARNING"
        else:
            result["overall_status"] = "FAIL"

        return result

    def test_all_skills(self) -> Dict:
        """Test all skills in the directory"""
        skill_dirs = [d for d in self.skills_dir.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_name = skill_dir.name
            self.results[skill_name] = self.test_skill(skill_name)

        return self.results

    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append("=" * 70)
        report.append(" Skill Execution Flow Test Report")
        report.append("=" * 70)
        report.append("")

        # Summary
        total_skills = len(self.results)
        passed = sum(1 for r in self.results.values() if r["overall_status"] == "PASS")
        warning = sum(1 for r in self.results.values() if r["overall_status"] == "WARNING")
        failed = sum(1 for r in self.results.values() if r["overall_status"] == "FAIL")

        report.append(f"Summary:")
        report.append(f"  Total Skills Tested: {total_skills}")
        report.append(f"  PASS: {passed} ✅")
        report.append(f"  WARNING: {warning} ⚠️")
        report.append(f"  FAIL: {failed} ❌")
        report.append("")

        # Individual results
        report.append("=" * 70)
        report.append(" Individual Skill Results")
        report.append("=" * 70)
        report.append("")

        for skill_name, result in sorted(self.results.items()):
            status_icon = {
                "PASS": "✅",
                "WARNING": "⚠️",
                "FAIL": "❌",
                "error": "🚨"
            }.get(result["overall_status"], "❓")

            report.append(f"{status_icon} {skill_name}")
            report.append(f"   Status: {result['overall_status']}")
            report.append(f"   Compliance: {result['compliance_percent']}% ({result['compliance_score']})")
            report.append("")

            # Detailed checks
            report.append("   Checks:")
            for check_name, passed in result["checks"].items():
                icon = "✅" if passed else "❌"
                report.append(f"     {icon} {check_name}")

            report.append("")

        # Recommendations
        report.append("=" * 70)
        report.append(" Recommendations")
        report.append("=" * 70)
        report.append("")

        for skill_name, result in self.results.items():
            if result["overall_status"] in ["FAIL", "WARNING"]:
                report.append(f"🔧 {skill_name}:")
                missing_checks = [name for name, passed in result["checks"].items() if not passed]
                for check in missing_checks:
                    report.append(f"   • Add: {check}")
                report.append("")

        return "\n".join(report)


def main():
    """Main test function"""
    skills_dir = "/root/.openclaw/workspace/skills"

    tester = SkillTester(skills_dir)
    results = tester.test_all_skills()
    report = tester.generate_report()

    print(report)

    # Save report to file
    report_file = Path("/root/.openclaw/workspace/skills/test_report.txt")
    report_file.write_text(report)
    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
