#!/usr/bin/env python3
"""
Download models from GitCode or HuggingFace with automatic fallback.
Priority: GitCode → huggingface.co → hf-mirror.com
"""

import argparse
import os
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from urllib.parse import quote

# GitCode configuration
GITCODE_BASE_URL = "https://gitcode.com/nicely235/place/-/raw/main"
GITCODE_MODELS = {
    "lerobot/smolvla_base": "models--lerobot--smolvla_base.tar.gz",
    "lerobot/pi05_base": "models--lerobot--pi05_base.tar.gz",
    "google/paligemma-3b-pt-224": "models--google--paligemma-3b-pt-224.tar.gz",
    "HuggingFaceTB/SmolVLM2-500M-Video-Instruct": "models--HuggingFaceTB--SmolVLM2-500M-Video-Instruct.tar.gz",
}

# HuggingFace mirrors
HF_MIRRORS = ["huggingface.co", "hf-mirror.com"]

# Cache directory
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"


def run_command(cmd, timeout=300, env=None):
    """Run shell command with timeout."""
    print(f"  执行: {cmd}")
    
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            timeout=timeout,
            capture_output=True,
            text=True,
            env=merged_env
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"


def download_from_gitcode(repo_id, cache_dir, timeout=120, proxy=None):
    """Download model from GitCode using git lfs."""
    print(f"\n🔄 Attempt 1: Trying GitCode (optimized for China)...")
    print(f"  Source: gitcode.com/nicely235/place")
    print(f"  Model: {repo_id}")
    
    if repo_id not in GITCODE_MODELS:
        print(f"  ⚠️  Model not available on GitCode: {repo_id}")
        print(f"  Available models: {', '.join(GITCODE_MODELS.keys())}")
        return False
    
    filename = GITCODE_MODELS[repo_id]
    
    # Create temporary directory for cloning
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        repo_dir = tmpdir_path / "place"
        
        print(f"  Method: git clone + git lfs pull")
        print(f"  Timeout: {timeout}s")
        
        # Set proxy environment
        env = {}
        if proxy:
            env["HTTP_PROXY"] = proxy
            env["HTTPS_PROXY"] = proxy
        
        # Step 1: Clone repository (without LFS files)
        print(f"  📥 Cloning repository...")
        # Skip automatic LFS download to speed up clone
        env["GIT_LFS_SKIP_SMUDGE"] = "1"
        cmd = f"git clone --depth 1 https://gitcode.com/nicely235/place.git {repo_dir}"
        success, stdout, stderr = run_command(cmd, timeout=60, env=env)
        
        if not success:
            print(f"  ❌ Clone failed: {stderr[:200]}")
            return False
        
        print(f"  ✅ Clone successful (LFS files not downloaded yet)")
        
        # Step 2: Pull specific LFS file
        print(f"  📥 Downloading LFS file: {filename}...")
        print(f"  ⏱️  This may take 1-3 minutes depending on file size...")
        os.chdir(repo_dir)
        
        # Pull only the specific file with extended timeout
        # SmolVLM2 is 910MB, smolvla_base is 686MB
        cmd = f"git lfs pull --include='{filename}'"
        success, stdout, stderr = run_command(cmd, timeout=timeout, env=env)
        
        if not success:
            print(f"  ❌ LFS pull failed: {stderr[:200]}")
            if "Timeout" in stderr or timeout <= 120:
                print(f"  💡 Tip: Try increasing --timeout (current: {timeout}s)")
            return False
        
        # Check if file exists
        lfs_file = repo_dir / filename
        if not lfs_file.exists() or lfs_file.stat().st_size == 0:
            print(f"  ❌ LFS file not found or empty")
            return False
        
        file_size_mb = lfs_file.stat().st_size / (1024 * 1024)
        print(f"  ✅ Download successful from GitCode")
        print(f"     Size: {file_size_mb:.1f}MB (compressed)")
        
        # Step 3: Extract tar.gz to cache directory
        print(f"  📦 Extracting...")
        try:
            with tarfile.open(lfs_file, 'r:gz') as tar:
                tar.extractall(path=cache_dir)
            print(f"  ✅ Extraction complete")
            print(f"  📁 Model saved to: {cache_dir}")
            return True
        except Exception as e:
            print(f"  ❌ Extraction failed: {e}")
            return False


def download_from_huggingface(repo_id, cache_dir, mirror="huggingface.co", timeout=300, proxy=None):
    """Download model from HuggingFace."""
    print(f"\n🔄 Attempt: Trying {mirror}...")
    print(f"  Source: {mirror}")
    print(f"  Repo: {repo_id}")
    print(f"  Timeout: {timeout}s")
    
    # Set environment
    env = {}
    if mirror != "huggingface.co":
        env["HF_ENDPOINT"] = f"https://{mirror}"
    
    if proxy:
        env["HTTP_PROXY"] = proxy
        env["HTTPS_PROXY"] = proxy
    
    # Use huggingface-cli to download
    cmd = f"huggingface-cli download {repo_id}"
    success, stdout, stderr = run_command(cmd, timeout=timeout, env=env)
    
    if success:
        print(f"  ✅ Download successful from {mirror}")
        return True
    else:
        print(f"  ❌ Download failed from {mirror}")
        if "Timeout" in stderr:
            print(f"     Reason: Timeout (>{timeout}s)")
        elif stderr:
            print(f"     Error: {stderr[:200]}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download models from GitCode or HuggingFace with automatic fallback"
    )
    parser.add_argument(
        "--repo-id",
        required=True,
        help="Model repository ID (e.g., lerobot/smolvla_base)"
    )
    parser.add_argument(
        "--cache-dir",
        default=str(DEFAULT_CACHE_DIR),
        help=f"Cache directory (default: {DEFAULT_CACHE_DIR})"
    )
    parser.add_argument(
        "--gitcode-url",
        default=GITCODE_BASE_URL,
        help="GitCode base URL"
    )
    parser.add_argument(
        "--proxy",
        help="Proxy URL (e.g., http://127.0.0.1:10809)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Download timeout in seconds (default: 300)"
    )
    parser.add_argument(
        "--skip-gitcode",
        action="store_true",
        help="Skip GitCode and download from HuggingFace directly"
    )
    parser.add_argument(
        "--skip-hf-mirror",
        action="store_true",
        help="Skip hf-mirror.com fallback"
    )
    
    args = parser.parse_args()
    
    # Create cache directory
    cache_dir = Path(args.cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Model Download - {args.repo_id}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Cache Dir: {cache_dir}")
    print(f"  Proxy: {args.proxy or 'None'}")
    print(f"  Timeout: {args.timeout}s")
    
    start_time = time.time()
    
    # Strategy 1: Try GitCode first
    if not args.skip_gitcode:
        # Use full timeout for GitCode (can be large files)
        gitcode_timeout = args.timeout
        if download_from_gitcode(args.repo_id, cache_dir, timeout=gitcode_timeout, proxy=args.proxy):
            elapsed = time.time() - start_time
            print(f"\n✅ Model downloaded successfully from GitCode")
            print(f"   Time: {elapsed:.1f}s")
            return 0
    
    # Strategy 2: Try huggingface.co
    if download_from_huggingface(
        args.repo_id,
        cache_dir,
        mirror="huggingface.co",
        timeout=args.timeout,
        proxy=args.proxy
    ):
        elapsed = time.time() - start_time
        print(f"\n✅ Model downloaded successfully from huggingface.co")
        print(f"   Time: {elapsed:.1f}s")
        return 0
    
    # Strategy 3: Try hf-mirror.com
    if not args.skip_hf_mirror:
        if download_from_huggingface(
            args.repo_id,
            cache_dir,
            mirror="hf-mirror.com",
            timeout=args.timeout,
            proxy=args.proxy
        ):
            elapsed = time.time() - start_time
            print(f"\n✅ Model downloaded successfully from hf-mirror.com")
            print(f"   Time: {elapsed:.1f}s")
            return 0
    
    # All strategies failed
    print(f"\n❌ All download attempts failed")
    print(f"\n建议:")
    print(f"  1. 检查代理设置: --proxy http://127.0.0.1:10809")
    print(f"  2. 增加超时时间: --timeout 600")
    print(f"  3. 检查网络连接")
    print(f"  4. 确认模型名称正确: {args.repo_id}")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
