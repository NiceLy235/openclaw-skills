#!/usr/bin/env python3
"""
Detailed Skill Steps Test Script

Analyzes the actual step content and execution flow of OpenClaw skills.
"""

import re
from pathlib import Path
from typing import List, Dict

class SkillStepAnalyzer:
    """Analyze skill steps in detail"""

    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)

    def extract_steps(self, content: str, skill_name: str) -> List[Dict]:
        """Extract steps from skill content"""
        steps = []

        # Pattern for extracting steps (both English and Chinese)
        step_patterns = [
            r'(?:Step|步骤)\s*(\d+)[：:]\s*([^\n]+)',
            r'###\s*(?:Step|步骤)\s*(\d+)[:：]?\s*([^\n]+)',
            r'\*\*(?:Step|步骤)\s*(\d+)[:：]?\*\*\s*([^\n]+)',
            r'(?:Step|步骤)\s*(\d+)[：:]\n\s*\*\*([A-Z][A-Za-z]+|[^\*]+)\*\*'
        ]

        for pattern in step_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                step_num = match[0]
                step_title = match[1].strip()
                steps.append({
                    "number": int(step_num),
                    "title": step_title,
                    "source": pattern[:20] + "..."
                })

        # Also look for numbered lists
        numbered_list_pattern = r'^(\d+)\.\s*\*\*([^\*]+)\*\*'
        for match in re.finditer(numbered_list_pattern, content, re.MULTILINE):
            step_num = match.group(1)
            step_title = match.group(2).strip()
            steps.append({
                "number": int(step_num),
                "title": step_title,
                "source": "numbered_list"
            })

        # Remove duplicates and sort
        seen = set()
        unique_steps = []
        for step in sorted(steps, key=lambda x: x["number"]):
            key = f"{step['number']}-{step['title']}"
            if key not in seen:
                seen.add(key)
                unique_steps.append(step)

        return unique_steps

    def analyze_mandatory_rules(self, content: str, skill_name: str) -> Dict:
        """Analyze mandatory execution rules"""
        rules = {
            "has_mandatory_section": False,
            "has_sequential_execution": False,
            "has_progress_reporting": False,
            "has_verification": False,
            "has_stop_on_error": False,
            "has_user_confirmation": False,
            "rules_text": []
        }

        # Check for MANDATORY/CRITICAL sections
        mandatory_section_match = re.search(
            r'(?:^|\n)(?:##\s*|\*\*|###\s*)?(MANDATORY|CRITICAL)[^\n]*\n',
            content, re.MULTILINE | re.IGNORECASE
        )
        if mandatory_section_match:
            rules["has_mandatory_section"] = True

        # Extract rules content
        if mandatory_section_match:
            section_start = mandatory_section_match.start()
            # Find end of section (next major heading or end of content)
            next_heading = re.search(r'\n#{2,}\s+[^\n]+', content[section_start:])
            if next_heading:
                section_end = section_start + next_heading.start()
            else:
                section_end = len(content)
            rules_content = content[section_start:section_end]
            rules["rules_text"] = [line.strip() for line in rules_content.split('\n') if line.strip() and not line.strip().startswith('#')]

        # Check for specific rules
        rules["has_sequential_execution"] = bool(re.search(
            r'(sequential|顺序|按顺序|step.*order|执行顺序)',
            content, re.IGNORECASE
        ))

        rules["has_progress_reporting"] = bool(re.search(
            r'(progress.*report|进度.*报告|report.*step|每步.*报告)',
            content, re.IGNORECASE
        ))

        rules["has_verification"] = bool(re.search(
            r'(verification|验证|check.*after|每步.*验证)',
            content, re.IGNORECASE
        ))

        rules["has_stop_on_error"] = bool(re.search(
            r'(stop on error|停止.*错误|error.*stop|出错.*停止)',
            content, re.IGNORECASE
        ))

        rules["has_user_confirmation"] = bool(re.search(
            r'(user.*confirm|用户.*确认|等待.*确认|confirm.*before)',
            content, re.IGNORECASE
        ))

        return rules

    def analyze_skill(self, skill_name: str) -> Dict:
        """Analyze a single skill in detail"""
        skill_dir = self.skills_dir / skill_name
        skill_file = skill_dir / "SKILL.md"

        if not skill_file.exists():
            return {
                "name": skill_name,
                "error": "SKILL.md not found"
            }

        content = skill_file.read_text()

        result = {
            "name": skill_name,
            "steps": self.extract_steps(content, skill_name),
            "rules": self.analyze_mandatory_rules(content, skill_name)
        }

        return result

    def analyze_all_skills(self) -> Dict[str, Dict]:
        """Analyze all skills"""
        results = {}
        skill_dirs = [d for d in self.skills_dir.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_name = skill_dir.name
            results[skill_name] = self.analyze_skill(skill_name)

        return results

    def generate_detailed_report(self) -> str:
        """Generate detailed analysis report"""
        results = self.analyze_all_skills()
        report = []
        report.append("=" * 80)
        report.append(" Skill Steps Detailed Analysis Report")
        report.append("=" * 80)
        report.append("")

        for skill_name, result in sorted(results.items()):
            if "error" in result:
                report.append(f"❌ {skill_name}: {result['error']}")
                report.append("")
                continue

            report.append(f"📋 {skill_name}")
            report.append("-" * 80)

            # Rules Analysis
            rules = result["rules"]
            report.append("📌 Execution Rules:")
            rule_names = {
                "has_mandatory_section": "Has MANDATORY/CRITICAL section",
                "has_sequential_execution": "Sequential execution required",
                "has_progress_reporting": "Progress reporting required",
                "has_verification": "Verification steps required",
                "has_stop_on_error": "Stop on error rule",
                "has_user_confirmation": "User confirmation required"
            }

            for rule_key, rule_desc in rule_names.items():
                icon = "✅" if rules[rule_key] else "❌"
                report.append(f"  {icon} {rule_desc}")

            report.append("")

            # Steps Analysis
            steps = result["steps"]
            if steps:
                report.append(f"📊 Steps Found: {len(steps)}")
                for step in steps:
                    report.append(f"  {step['number']}. {step['title']}")
            else:
                report.append("  ⚠️ No steps detected")

            report.append("")
            report.append("")

        # Summary
        report.append("=" * 80)
        report.append(" Summary")
        report.append("=" * 80)

        total_skills = len(results)
        skills_with_steps = sum(1 for r in results.values() if "error" not in r and r.get("steps"))
        skills_with_mandatory = sum(1 for r in results.values() if "error" not in r and r.get("rules", {}).get("has_mandatory_section"))
        skills_with_stop_on_error = sum(1 for r in results.values() if "error" not in r and r.get("rules", {}).get("has_stop_on_error"))

        report.append(f"Total Skills: {total_skills}")
        report.append(f"Skills with Steps: {skills_with_steps}/{total_skills}")
        report.append(f"Skills with MANDATORY Rules: {skills_with_mandatory}/{total_skills}")
        report.append(f"Skills with Stop-on-Error: {skills_with_stop_on_error}/{total_skills}")

        return "\n".join(report)


def main():
    """Main function"""
    skills_dir = "/root/.openclaw/workspace/skills"
    analyzer = SkillStepAnalyzer(skills_dir)
    report = analyzer.generate_detailed_report()

    print(report)

    # Save report
    report_file = Path(skills_dir) / "detailed_steps_report.txt"
    report_file.write_text(report)
    print(f"\nDetailed report saved to: {report_file}")


if __name__ == "__main__":
    main()
