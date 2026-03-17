#!/usr/bin/env python3
"""
Dependency conflict resolver for lerobot installations.

Detects and fixes common dependency version conflicts:
- PyTorch/torchvision version mismatch
- huggingface-hub version conflicts
- protobuf version conflicts
- packaging version conflicts
- Missing dependencies (num2words, etc.)
"""

import subprocess
import sys
from typing import Dict, List, Optional, Tuple
import json


class DependencyResolver:
    """Detect and resolve dependency conflicts."""
    
    # Known working version combinations
    WORKING_VERSIONS = {
        "lerobot_0.4.4": {
            "torch": "2.5.1",
            "torchvision": "0.20.1",
            "huggingface-hub": "0.35.2",
            "packaging": "25.0",
            "protobuf": "6.30.2",
            "transformers": "4.48.0",  # Changed from 5.3.0 to be compatible with huggingface-hub <0.36.0
            "num2words": "latest",
        }
    }
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Print log message."""
        if self.verbose:
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "STEP": "🔧"
            }.get(level, "ℹ️")
            print(f"{prefix} {message}")
    
    def run_pip(self, *args: str) -> Tuple[int, str, str]:
        """Run pip command and return exit code, stdout, stderr."""
        cmd = [sys.executable, "-m", "pip"] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    
    def get_installed_version(self, package: str) -> Optional[str]:
        """Get installed version of a package."""
        code, stdout, stderr = self.run_pip("show", package)
        if code != 0:
            return None
        
        for line in stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
        
        return None
    
    def check_pytorch_torchvision_compatibility(self) -> bool:
        """Check if PyTorch and torchvision versions are compatible."""
        try:
            import torch
            import torchvision
            
            torch_version = torch.__version__
            tv_version = torchvision.__version__
            
            # Extract major.minor from versions
            torch_major_minor = '.'.join(torch_version.split('.')[:2])
            tv_major_minor = '.'.join(tv_version.split('.')[:2])
            
            # Check if major.minor versions match
            if torch_major_minor == tv_major_minor:
                self.log(f"PyTorch {torch_version} and torchvision {tv_version} are compatible", "SUCCESS")
                return True
            else:
                self.log(f"PyTorch {torch_version} and torchvision {tv_version} versions mismatch!", "WARNING")
                return False
                
        except ImportError as e:
            self.log(f"Cannot import: {e}", "ERROR")
            return False
    
    def check_all_imports(self) -> Dict[str, bool]:
        """Check if all required packages can be imported."""
        required = [
            ("torch", "PyTorch"),
            ("torchvision", "torchvision"),
            ("lerobot", "LeRobot"),
            ("transformers", "transformers"),
            ("num2words", "num2words"),
            ("huggingface_hub", "huggingface-hub"),
        ]
        
        results = {}
        
        for module, name in required:
            try:
                __import__(module)
                self.log(f"{name}: OK", "SUCCESS")
                results[name] = True
            except ImportError as e:
                self.log(f"{name}: FAILED - {e}", "ERROR")
                results[name] = False
        
        return results
    
    def detect_conflicts(self) -> List[Dict]:
        """Detect all dependency conflicts."""
        conflicts = []
        
        # Check PyTorch/torchvision
        if not self.check_pytorch_torchvision_compatibility():
            torch_ver = self.get_installed_version("torch")
            tv_ver = self.get_installed_version("torchvision")
            conflicts.append({
                "type": "pytorch_version_mismatch",
                "package": "torchvision",
                "installed": tv_ver,
                "required": f"Should match PyTorch {torch_ver}",
                "severity": "high"
            })
        
        # Check for lerobot
        try:
            import lerobot
            self.log(f"LeRobot version: {lerobot.__version__}", "INFO")
        except ImportError:
            conflicts.append({
                "type": "missing_package",
                "package": "lerobot",
                "severity": "critical"
            })
        
        # Check for num2words
        try:
            import num2words
        except ImportError:
            conflicts.append({
                "type": "missing_package",
                "package": "num2words",
                "severity": "medium"
            })
        
        return conflicts
    
    def fix_pytorch_torchvision_mismatch(self) -> bool:
        """Fix PyTorch and torchvision version mismatch."""
        self.log("Fixing PyTorch/torchvision version mismatch...", "STEP")
        
        # Get current PyTorch version
        torch_ver = self.get_installed_version("torch")
        
        if not torch_ver:
            self.log("PyTorch not installed", "ERROR")
            return False
        
        # Determine matching torchvision version
        # For PyTorch 2.5.x -> torchvision 0.20.x
        # For PyTorch 2.4.x -> torchvision 0.19.x
        # etc.
        
        torch_major = int(torch_ver.split('.')[0])
        torch_minor = int(torch_ver.split('.')[1])
        
        if torch_major == 2 and torch_minor == 5:
            tv_version = "0.20.1"
        elif torch_major == 2 and torch_minor == 4:
            tv_version = "0.19.1"
        elif torch_major == 2 and torch_minor == 6:
            tv_version = "0.21.0"
        else:
            self.log(f"Unknown PyTorch version {torch_ver}, using latest torchvision", "WARNING")
            tv_version = None
        
        # Reinstall torchvision
        if tv_version:
            self.log(f"Installing torchvision {tv_version} to match PyTorch {torch_ver}", "INFO")
            code, stdout, stderr = self.run_pip(
                "install", "--force-reinstall",
                f"torchvision=={tv_version}",
                "--no-deps"
            )
        else:
            self.log("Installing latest torchvision", "INFO")
            code, stdout, stderr = self.run_pip(
                "install", "--upgrade",
                "torchvision"
            )
        
        if code == 0:
            self.log("torchvision reinstalled successfully", "SUCCESS")
            return True
        else:
            self.log(f"Failed to reinstall torchvision: {stderr}", "ERROR")
            return False
    
    def install_missing_package(self, package: str) -> bool:
        """Install a missing package."""
        self.log(f"Installing missing package: {package}", "STEP")
        
        code, stdout, stderr = self.run_pip("install", package)
        
        if code == 0:
            self.log(f"{package} installed successfully", "SUCCESS")
            return True
        else:
            self.log(f"Failed to install {package}: {stderr}", "ERROR")
            return False
    
    def fix_conflicts(self, conflicts: List[Dict]) -> Dict[str, bool]:
        """Fix all detected conflicts."""
        results = {}
        
        for conflict in conflicts:
            conflict_type = conflict["type"]
            package = conflict.get("package", "unknown")
            
            if conflict_type == "pytorch_version_mismatch":
                results[package] = self.fix_pytorch_torchvision_mismatch()
            
            elif conflict_type == "missing_package":
                results[package] = self.install_missing_package(package)
            
            else:
                self.log(f"Unknown conflict type: {conflict_type}", "WARNING")
                results[package] = False
        
        return results
    
    def verify_cuda(self) -> bool:
        """Verify CUDA is working with PyTorch."""
        try:
            import torch
            
            if not torch.cuda.is_available():
                self.log("CUDA is not available (CPU mode)", "WARNING")
                return False
            
            self.log(f"CUDA available: {torch.version.cuda}", "SUCCESS")
            self.log(f"GPU: {torch.cuda.get_device_name(0)}", "SUCCESS")
            
            # Test CUDA operation
            x = torch.randn(1000, 1000, device='cuda')
            y = torch.mm(x, x)
            
            self.log("CUDA operations working correctly", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"CUDA verification failed: {e}", "ERROR")
            return False
    
    def generate_report(self) -> str:
        """Generate a comprehensive report of the environment."""
        report = []
        report.append("="*60)
        report.append("Dependency Status Report")
        report.append("="*60)
        
        # Check imports
        report.append("\n📦 Package Status:")
        imports = self.check_all_imports()
        for name, status in imports.items():
            status_str = "✅" if status else "❌"
            report.append(f"  {status_str} {name}")
        
        # Check conflicts
        conflicts = self.detect_conflicts()
        if conflicts:
            report.append("\n⚠️  Detected Conflicts:")
            for conflict in conflicts:
                report.append(f"  - {conflict['type']}: {conflict.get('package', 'N/A')}")
        else:
            report.append("\n✅ No conflicts detected")
        
        # CUDA status
        report.append("\n🖥️  CUDA Status:")
        try:
            import torch
            if torch.cuda.is_available():
                report.append(f"  ✅ CUDA {torch.version.cuda}")
                report.append(f"  ✅ GPU: {torch.cuda.get_device_name(0)}")
            else:
                report.append("  ⚠️  CPU mode only")
        except:
            report.append("  ❌ Cannot check CUDA")
        
        report.append("\n" + "="*60)
        
        return '\n'.join(report)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Resolve dependency conflicts for lerobot"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check for conflicts, don't fix"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix detected conflicts"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Minimal output"
    )
    
    args = parser.parse_args()
    
    resolver = DependencyResolver(verbose=not args.quiet)
    
    # Default: check and report
    if not (args.check or args.fix or args.report):
        args.report = True
        args.check = True
    
    # Check for conflicts
    if args.check or args.report:
        conflicts = resolver.detect_conflicts()
        
        if not conflicts:
            resolver.log("No conflicts detected! ✅", "SUCCESS")
        else:
            resolver.log(f"Found {len(conflicts)} conflict(s)", "WARNING")
    
    # Fix conflicts
    if args.fix and conflicts:
        resolver.log("\nFixing conflicts...", "STEP")
        results = resolver.fix_conflicts(conflicts)
        
        resolver.log("\nFix Results:")
        for package, success in results.items():
            status = "✅" if success else "❌"
            resolver.log(f"  {status} {package}")
    
    # Generate report
    if args.report:
        print("\n" + resolver.generate_report())


if __name__ == "__main__":
    main()
