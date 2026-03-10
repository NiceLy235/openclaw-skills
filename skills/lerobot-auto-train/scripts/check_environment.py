#!/usr/bin/env python3
"""
Environment checker for lerobot_ros2 training automation.

Performs comprehensive checks and optional auto-fix for:
- Repository context (must be in lerobot_ros2)
- Python environment
- CUDA availability
- Dependencies
- Configuration files
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class EnvironmentChecker:
    """Check and optionally fix training environment."""

    def __init__(self, repo_path: Optional[str] = None, auto_fix: bool = False):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.auto_fix = auto_fix
        self.results = {
            "environment_check": {
                "in_lerobot_repo": False,
                "python_env_active": False,
                "cuda_available": False,
                "cuda_version": None,
                "dependencies": {
                    "status": "unknown",
                    "installed": [],
                    "missing": [],
                    "can_auto_install": False
                },
                "configs": {
                    "status": "unknown",
                    "training_config": "missing",
                    "model_def": "missing"
                },
                "overall_status": "checking",
                "fix_suggestions": []
            }
        }

    def check_all(self) -> Dict:
        """Run all environment checks."""
        print("🔍 Checking training environment...")

        # Step 1: Repository check
        self._check_repository()
        if not self.results["environment_check"]["in_lerobot_repo"]:
            # Critical failure - can't continue
            self.results["environment_check"]["overall_status"] = "failed"
            return self.results

        # Step 2: Python environment
        self._check_python_env()

        # Step 3: CUDA
        self._check_cuda()

        # Step 4: Dependencies
        self._check_dependencies()

        # Step 5: Configuration
        self._check_configs()

        # Determine overall status
        self._determine_overall_status()

        return self.results

    def _check_repository(self) -> None:
        """Check if we're in a lerobot_ros2 repository."""
        print("  [1/5] Checking repository context...", end=" ")

        try:
            # Check if .git exists
            git_dir = self.repo_path / ".git"
            if not git_dir.exists():
                self.results["environment_check"]["in_lerobot_repo"] = False
                self.results["environment_check"]["fix_suggestions"].append(
                    "Not in a git repository. Navigate to lerobot_ros2 directory first."
                )
                print("❌ Not a git repository")
                return

            # Check remote origin or directory name
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            is_lerobot_repo = (
                "lerobot_ros2" in self.repo_path.name or
                (result.returncode == 0 and "lerobot_ros2" in result.stdout)
            )

            self.results["environment_check"]["in_lerobot_repo"] = is_lerobot_repo

            if is_lerobot_repo:
                print("✅ In lerobot_ros2 repository")
            else:
                print("❌ Not in lerobot_ros2 repository")
                self.results["environment_check"]["fix_suggestions"].append(
                    f"Current directory: {self.repo_path}. "
                    f"Please cd to lerobot_ros2 repository or use --repo-path"
                )

        except Exception as e:
            self.results["environment_check"]["in_lerobot_repo"] = False
            self.results["environment_check"]["fix_suggestions"].append(
                f"Repository check failed: {str(e)}"
            )
            print(f"❌ Error: {e}")

    def _check_python_env(self) -> None:
        """Check if Python virtual environment is active."""
        print("  [2/5] Checking Python environment...", end=" ")

        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            os.environ.get('CONDA_DEFAULT_ENV') is not None
        )

        self.results["environment_check"]["python_env_active"] = in_venv

        if in_venv:
            env_name = os.environ.get('CONDA_DEFAULT_ENV', os.path.basename(sys.prefix))
            print(f"✅ Active: {env_name}")
        else:
            print("⚠️  No virtual environment active")
            self.results["environment_check"]["fix_suggestions"].append(
                "No virtual environment detected. Consider activating one: "
                "`conda activate <env>` or `source <venv>/bin/activate`"
            )

    def _check_cuda(self) -> None:
        """Check CUDA availability."""
        print("  [3/5] Checking CUDA...", end=" ")

        try:
            import torch
            cuda_available = torch.cuda.is_available()

            self.results["environment_check"]["cuda_available"] = cuda_available

            if cuda_available:
                cuda_version = torch.version.cuda
                self.results["environment_check"]["cuda_version"] = cuda_version
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
                print(f"✅ CUDA {cuda_version} - {gpu_name} ({gpu_count} GPU(s))")
            else:
                print("❌ CUDA not available")
                self.results["environment_check"]["fix_suggestions"].append(
                    "CUDA not available. Check NVIDIA driver installation or use CPU mode."
                )

        except ImportError:
            print("❌ PyTorch not installed")
            self.results["environment_check"]["cuda_available"] = False
            self.results["environment_check"]["fix_suggestions"].append(
                "PyTorch not installed. Install with: pip install torch torchvision"
            )

    def _check_dependencies(self) -> None:
        """Check required dependencies."""
        print("  [4/5] Checking dependencies...", end=" ")

        required_packages = [
            "torch", "numpy", "gym", "lerobot", "transformers",
            "datasets", "wandb", "tensorboard"
        ]

        installed = []
        missing = []

        for package in required_packages:
            try:
                __import__(package)
                installed.append(package)
            except ImportError:
                missing.append(package)

        deps = self.results["environment_check"]["dependencies"]
        deps["installed"] = installed
        deps["missing"] = missing
        deps["status"] = "complete" if not missing else "incomplete"
        deps["can_auto_install"] = True

        if missing:
            print(f"⚠️  Missing {len(missing)} packages")
            deps["fix_suggestions"] = [
                f"pip install {' '.join(missing)}",
                "or use --auto-fix to install automatically"
            ]
        else:
            print(f"✅ All {len(installed)} packages installed")

    def _check_configs(self) -> None:
        """Check configuration files."""
        print("  [5/5] Checking configuration files...", end=" ")

        configs = self.results["environment_check"]["configs"]

        # Check training config
        training_config_paths = [
            self.repo_path / "config" / "training_config.yaml",
            self.repo_path / "config" / "training_config.default.yaml",
        ]

        for path in training_config_paths:
            if path.exists():
                configs["training_config"] = "exists"
                break
        else:
            configs["training_config"] = "missing"
            self.results["environment_check"]["fix_suggestions"].append(
                "Training config missing. Copy default: "
                "cp config/training_config.default.yaml config/training_config.yaml"
            )

        # Check model definition
        model_dirs = ["models", "policies"]
        has_model = any((self.repo_path / d).exists() for d in model_dirs)
        configs["model_def"] = "exists" if has_model else "missing"

        if not has_model:
            self.results["environment_check"]["fix_suggestions"].append(
                "Model definition directory not found. "
                "Expected 'models/' or 'policies/' directory."
            )

        all_ok = (
            configs["training_config"] == "exists" and
            configs["model_def"] == "exists"
        )

        configs["status"] = "ok" if all_ok else "incomplete"

        if all_ok:
            print("✅ All configs present")
        else:
            print("⚠️  Some configs missing")

    def _determine_overall_status(self) -> None:
        """Determine overall environment status."""
        env = self.results["environment_check"]

        # Must-have checks
        critical_checks = [
            env["in_lerobot_repo"],
        ]

        # Important but can continue
        important_checks = [
            env["python_env_active"],
            env["cuda_available"],
            env["dependencies"]["status"] == "complete",
            env["configs"]["status"] == "ok",
        ]

        if not all(critical_checks):
            env["overall_status"] = "failed"
        elif all(important_checks):
            env["overall_status"] = "ready"
        else:
            env["overall_status"] = "needs_fix"

    def auto_fix(self) -> None:
        """Attempt to automatically fix environment issues."""
        if not self.auto_fix:
            return

        print("\n🔧 Auto-fixing environment issues...")

        # Fix dependencies
        missing = self.results["environment_check"]["dependencies"]["missing"]
        if missing:
            print(f"  Installing missing packages: {', '.join(missing)}")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + missing,
                    check=True
                )
                print("  ✅ Dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install dependencies: {e}")
                self.results["environment_check"]["fix_suggestions"].append(
                    f"Auto-fix failed. Manual install required: pip install {' '.join(missing)}"
                )

    def print_report(self) -> None:
        """Print human-readable report."""
        env = self.results["environment_check"]

        print("\n" + "="*60)
        print("ENVIRONMENT CHECK REPORT")
        print("="*60)

        # Status
        status_icon = {
            "ready": "✅",
            "needs_fix": "⚠️ ",
            "failed": "❌",
            "checking": "🔍"
        }.get(env["overall_status"], "❓")

        print(f"\nOverall Status: {status_icon} {env['overall_status'].upper()}")

        # Details
        print(f"\nRepository:")
        print(f"  - In lerobot_ros2: {'✅' if env['in_lerobot_repo'] else '❌'}")

        print(f"\nPython Environment:")
        print(f"  - Virtual env active: {'✅' if env['python_env_active'] else '❌'}")

        print(f"\nCUDA:")
        if env["cuda_available"]:
            print(f"  - Available: ✅ (version {env['cuda_version']})")
        else:
            print(f"  - Available: ❌")

        print(f"\nDependencies:")
        deps = env["dependencies"]
        print(f"  - Installed ({len(deps['installed'])}): {', '.join(deps['installed'])}")
        if deps["missing"]:
            print(f"  - Missing ({len(deps['missing'])}): {', '.join(deps['missing'])}")

        print(f"\nConfiguration:")
        cfg = env["configs"]
        print(f"  - Training config: {cfg['training_config']}")
        print(f"  - Model definition: {cfg['model_def']}")

        # Suggestions
        if env["fix_suggestions"]:
            print(f"\n💡 Fix Suggestions:")
            for i, suggestion in enumerate(env["fix_suggestions"], 1):
                print(f"  {i}. {suggestion}")

        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Check and optionally fix training environment"
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        help="Path to lerobot_ros2 repository (default: current directory)"
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically fix environment issues"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check only, don't fix (output as JSON)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Run checks
    checker = EnvironmentChecker(
        repo_path=args.repo_path,
        auto_fix=args.auto_fix and not args.dry_run
    )

    results = checker.check_all()

    # Auto-fix if requested
    if args.auto_fix and not args.dry_run:
        checker.auto_fix()
        # Re-check after fixes
        results = checker.check_all()

    # Output
    if args.json or args.dry_run:
        print(json.dumps(results, indent=2))
    else:
        checker.print_report()

    # Exit with appropriate code
    if results["environment_check"]["overall_status"] == "ready":
        sys.exit(0)
    elif results["environment_check"]["overall_status"] == "needs_fix":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
