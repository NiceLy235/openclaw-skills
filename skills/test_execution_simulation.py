#!/usr/bin/env python3
"""
Skill Execution Simulation Test

Simulates how an AI agent would execute each skill following its defined steps.
This tests whether the skills have clear, executable step-by-step instructions.
"""

import re
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Step:
    """Represents a single execution step"""
    number: int
    title: str
    action: str
    command: str
    expected: str

class SkillExecutionSimulator:
    """Simulate skill execution flow"""

    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)

    def parse_execution_steps(self, content: str) -> List[Step]:
        """Parse executable steps from skill content"""
        steps = []

        # Look for code blocks with step-by-step execution
        code_blocks = re.findall(r'```(?:bash|python|sh)\n(.*?)```', content, re.DOTALL)

        for block in code_blocks:
            lines = [line.strip() for line in block.split('\n') if line.strip() and not line.strip().startswith('#')]

            # Group lines into logical steps
            current_step = None
            for i, line in enumerate(lines):
                if line.startswith('#') or 'Step' in line or '步骤' in line:
                    if current_step:
                        steps.append(current_step)
                    # Extract step number
                    step_match = re.search(r'(?:Step|步骤)\s*(\d+)', line, re.IGNORECASE)
                    step_num = int(step_match.group(1)) if step_match else len(steps) + 1
                    current_step = Step(
                        number=step_num,
                        title=line,
                        action="",
                        command=line,
                        expected=""
                    )
                elif current_step:
                    if not current_step.action:
                        current_step.action = line
                    elif not current_step.command or line.startswith('$'):
                        current_step.command = line
                    elif not current_step.expected:
                        current_step.expected = line

            if current_step:
                steps.append(current_step)

        # If no code blocks, look for markdown lists with commands
        if not steps:
            # Look for patterns like: Step X: [Title] - [Command]
            step_pattern = r'(?:Step|步骤)\s*(\d+)[:：]\s*([^\n-]+)(?:\s*-\s*([^$\n]+))?'
            for match in re.finditer(step_pattern, content, re.IGNORECASE):
                step_num = int(match.group(1))
                title = match.group(2).strip()
                command = match.group(3).strip() if match.group(3) else ""
                steps.append(Step(step_num, title, "", command, ""))

        return steps

    def check_mandatory_prerequisites(self, content: str) -> Dict:
        """Check if skill defines mandatory prerequisites"""
        prereqs = {
            "has_prerequisite_check": False,
            "has_pre_install_check": False,
            "has_dependency_check": False,
            "has_network_check": False,
            "has_user_input_required": False
        }

        prereq_patterns = {
            "has_prerequisite_check": r'(prerequisite|前置要求|before.*proceeding|must.*first)',
            "has_pre_install_check": r'(before.*install|install.*check|安装前.*检查)',
            "has_dependency_check": r'(dependency.*check|检查.*依赖|依赖.*检查)',
            "has_network_check": r'(network.*check|connectivity.*test|网络.*检查|代理.*测试)',
            "has_user_input_required": r'(ask.*user|user.*input|用户.*确认|required.*input|必填)'
        }

        for key, pattern in prereq_patterns.items():
            prereqs[key] = bool(re.search(pattern, content, re.IGNORECASE))

        return prereqs

    def check_error_handling(self, content: str) -> Dict:
        """Check if skill has error handling rules"""
        error_handling = {
            "has_error_detection": False,
            "has_error_recovery": False,
            "has_error_reporting": False,
            "has_stop_on_error": False,
            "has_retry_logic": False
        }

        error_patterns = {
            "has_error_detection": r'(detect.*error|error.*detection|check.*error)',
            "has_error_recovery": r'(recover|fix.*error|solve|solution|恢复|解决)',
            "has_error_reporting": r'(report.*error|error.*report|reporting)',
            "has_stop_on_error": r'(stop on error|stop.*failed|出错.*停止|failed.*stop)',
            "has_retry_logic": r'(retry|重试|re.*attempt)'
        }

        for key, pattern in error_patterns.items():
            error_handling[key] = bool(re.search(pattern, content, re.IGNORECASE))

        return error_handling

    def check_progress_tracking(self, content: str) -> Dict:
        """Check if skill has progress tracking"""
        progress = {
            "has_progress_reporting": False,
            "has_progress_percentage": False,
            "has_step_completion_notification": False,
            "has_time_estimate": False
        }

        progress_patterns = {
            "has_progress_reporting": r'(progress.*report|report.*progress|进度.*报告)',
            "has_progress_percentage": r'(\d+%|percentage)',
            "has_step_completion_notification": r'(step.*complete|complete.*step|report.*after.*step)',
            "has_time_estimate": r'(estimated.*time|time.*estimate|预计.*时间|耗时)'
        }

        for key, pattern in progress_patterns.items():
            progress[key] = bool(re.search(pattern, content, re.IGNORECASE))

        return progress

    def simulate_execution(self, skill_name: str) -> Dict:
        """Simulate executing the skill step by step"""
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
            "steps": self.parse_execution_steps(content),
            "prerequisites": self.check_mandatory_prerequisites(content),
            "error_handling": self.check_error_handling(content),
            "progress_tracking": self.check_progress_tracking(content),
            "execution_score": 0
        }

        # Calculate execution score (0-100)
        checks = [
            (len(result["steps"]) > 0, 20, "Has executable steps"),
            (result["prerequisites"]["has_prerequisite_check"], 15, "Has prerequisite checks"),
            (result["prerequisites"]["has_user_input_required"], 10, "Requires user input"),
            (result["error_handling"]["has_stop_on_error"], 15, "Stop on error rule"),
            (result["error_handling"]["has_error_recovery"], 10, "Error recovery"),
            (result["progress_tracking"]["has_progress_reporting"], 15, "Progress reporting"),
            (result["progress_tracking"]["has_step_completion_notification"], 15, "Step completion notification")
        ]

        total_score = 0
        for check, weight, description in checks:
            if check:
                total_score += weight

        result["execution_score"] = total_score
        result["execution_checks"] = [
            {"description": desc, "passed": check, "weight": weight}
            for check, weight, desc in checks
        ]

        return result

    def run_all_simulations(self) -> Dict[str, Dict]:
        """Run execution simulation for all skills"""
        results = {}
        skill_dirs = [d for d in self.skills_dir.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_name = skill_dir.name
            results[skill_name] = self.simulate_execution(skill_name)

        return results

    def generate_simulation_report(self) -> str:
        """Generate simulation execution report"""
        results = self.run_all_simulations()
        report = []
        report.append("=" * 80)
        report.append(" Skill Execution Simulation Report")
        report.append(" Simulates step-by-step execution of each skill")
        report.append("=" * 80)
        report.append("")

        for skill_name, result in sorted(results.items()):
            if result["status"] == "error":
                report.append(f"❌ {skill_name}: {result['message']}")
                report.append("")
                continue

            # Determine grade
            score = result["execution_score"]
            if score >= 80:
                grade = "A ✅"
                grade_desc = "Excellent execution flow"
            elif score >= 60:
                grade = "B ⚠️"
                grade_desc = "Good, needs some improvements"
            elif score >= 40:
                grade = "C ⚠️"
                grade_desc = "Fair, significant improvements needed"
            else:
                grade = "D ❌"
                grade_desc = "Poor, needs major improvements"

            report.append(f"📊 {skill_name} - Grade: {grade}")
            report.append(f"   Score: {score}/100 - {grade_desc}")
            report.append("")

            # Execution checks
            report.append("   Execution Checks:")
            for check in result["execution_checks"]:
                icon = "✅" if check["passed"] else "❌"
                report.append(f"     {icon} {check['description']} ({check['weight']} pts)")
            report.append("")

            # Prerequisites
            prereqs = result["prerequisites"]
            report.append("   Prerequisites:")
            prereq_names = {
                "has_prerequisite_check": "Prerequisite checks",
                "has_pre_install_check": "Pre-install checks",
                "has_dependency_check": "Dependency checks",
                "has_network_check": "Network/connectivity checks",
                "has_user_input_required": "Requires user input"
            }
            for key, name in prereq_names.items():
                icon = "✅" if prereqs[key] else "❌"
                report.append(f"     {icon} {name}")
            report.append("")

            # Error Handling
            err_handle = result["error_handling"]
            report.append("   Error Handling:")
            err_names = {
                "has_error_detection": "Error detection",
                "has_error_recovery": "Error recovery",
                "has_error_reporting": "Error reporting",
                "has_stop_on_error": "Stop on error",
                "has_retry_logic": "Retry logic"
            }
            for key, name in err_names.items():
                icon = "✅" if err_handle[key] else "❌"
                report.append(f"     {icon} {name}")
            report.append("")

            # Progress Tracking
            progress = result["progress_tracking"]
            report.append("   Progress Tracking:")
            prog_names = {
                "has_progress_reporting": "Progress reporting",
                "has_progress_percentage": "Progress percentage",
                "has_step_completion_notification": "Step completion notification",
                "has_time_estimate": "Time estimates"
            }
            for key, name in prog_names.items():
                icon = "✅" if progress[key] else "❌"
                report.append(f"     {icon} {name}")
            report.append("")

            # Steps
            steps = result["steps"]
            if steps:
                report.append(f"   Executable Steps Found: {len(steps)}")
                for i, step in enumerate(steps[:5], 1):  # Show first 5
                    report.append(f"     {i}. {step.title}")
                if len(steps) > 5:
                    report.append(f"     ... and {len(steps) - 5} more")
            else:
                report.append("   ⚠️ No executable steps detected")
            report.append("")

        # Summary
        report.append("=" * 80)
        report.append(" Summary")
        report.append("=" * 80)

        valid_results = [r for r in results.values() if r["status"] == "success"]
        if valid_results:
            avg_score = sum(r["execution_score"] for r in valid_results) / len(valid_results)
            report.append(f"Average Execution Score: {avg_score:.1f}/100")

        report.append("")
        report.append("Recommendations:")

        for skill_name, result in results.items():
            if result["status"] == "success" and result["execution_score"] < 80:
                report.append(f"\n🔧 {skill_name}:")
                report.append(f"   Current Score: {result['execution_score']}/100")
                report.append("   Improvements needed:")

                if not result["error_handling"]["has_stop_on_error"]:
                    report.append("   • Add 'stop on error' rule")
                if not result["progress_tracking"]["has_progress_reporting"]:
                    report.append("   • Add progress reporting")
                if not result["prerequisites"]["has_prerequisite_check"]:
                    report.append("   • Add prerequisite checks")
                if len(result["steps"]) == 0:
                    report.append("   • Define executable steps")

        return "\n".join(report)


def main():
    """Main function"""
    skills_dir = "/root/.openclaw/workspace/skills"
    simulator = SkillExecutionSimulator(skills_dir)
    report = simulator.generate_simulation_report()

    print(report)

    # Save report
    report_file = Path(skills_dir) / "execution_simulation_report.txt"
    report_file.write_text(report)
    print(f"\nExecution simulation report saved to: {report_file}")


if __name__ == "__main__":
    main()
