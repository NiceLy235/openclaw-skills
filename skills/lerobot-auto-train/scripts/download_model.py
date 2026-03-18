#!/usr/bin/env python3
"""
Download models from HuggingFace with automatic mirror fallback.

Usage:
    python download_model.py --repo-id lerobot/smolvla_base --proxy http://127.0.0.1:10809

Features:
- First try huggingface.co
- If failed or timeout, fallback to hf-mirror.com
- Support proxy configuration
- Progress tracking
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def download_from_huggingface(
    repo_id: str,
    proxy: str = None,
    hf_token: str = None,
    timeout: int = 300,
    use_mirror: bool = False
) -> bool:
    """
    Download model from HuggingFace or mirror.
    
    Args:
        repo_id: HuggingFace repo ID (e.g., lerobot/smolvla_base)
        proxy: Proxy URL (e.g., http://127.0.0.1:10809)
        hf_token: HuggingFace token
        timeout: Download timeout in seconds
        use_mirror: Whether to use hf-mirror.com
    
    Returns:
        True if successful
    """
    # Set environment variables
    env = os.environ.copy()
    
    if proxy:
        env["HTTP_PROXY"] = proxy
        env["HTTPS_PROXY"] = proxy
    
    if hf_token:
        env["HF_TOKEN"] = hf_token
    
    # Set mirror endpoint if needed
    if use_mirror:
        env["HF_ENDPOINT"] = "https://hf-mirror.com"
        source = "hf-mirror.com"
    else:
        env["HF_ENDPOINT"] = "https://huggingface.co"
        source = "huggingface.co"
    
    print(f"  Source: {source}")
    print(f"  Repo: {repo_id}")
    print(f"  Timeout: {timeout}s")
    
    # Build huggingface-cli command
    cmd = [
        "huggingface-cli", "download",
        repo_id,
        "--local-dir", os.path.expanduser(f"~/.cache/huggingface/hub/models--{repo_id.replace('/', '--')}"),
    ]
    
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ Download successful from {source}")
            print(f"   Time: {elapsed:.1f}s")
            if result.stdout:
                print(result.stdout[-500:])  # Last 500 chars
            return True
        else:
            print(f"❌ Download failed from {source}")
            print(f"   Error: {result.stderr[-500:]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Download timeout from {source} (>{timeout}s)")
        return False
    except Exception as e:
        print(f"❌ Download error from {source}: {e}")
        return False


def download_with_fallback(
    repo_id: str,
    proxy: str = None,
    hf_token: str = None,
    timeout: int = 300
) -> dict:
    """
    Download with automatic mirror fallback.
    
    Returns:
        {
            "success": bool,
            "source": str,  # "huggingface.co" or "hf-mirror.com"
            "attempts": int
        }
    """
    result = {
        "success": False,
        "source": None,
        "attempts": 0
    }
    
    # Attempt 1: Try huggingface.co
    result["attempts"] += 1
    print(f"\n🔄 Attempt {result['attempts']}: Trying huggingface.co...")
    
    if download_from_huggingface(
        repo_id=repo_id,
        proxy=proxy,
        hf_token=hf_token,
        timeout=timeout,
        use_mirror=False
    ):
        result["success"] = True
        result["source"] = "huggingface.co"
        return result
    
    # Attempt 2: Fallback to hf-mirror.com
    result["attempts"] += 1
    print(f"\n🔄 Attempt {result['attempts']}: Falling back to hf-mirror.com...")
    
    if download_from_huggingface(
        repo_id=repo_id,
        proxy=proxy,
        hf_token=hf_token,
        timeout=timeout,
        use_mirror=True
    ):
        result["success"] = True
        result["source"] = "hf-mirror.com"
        return result
    
    # Both failed
    print(f"\n❌ All download attempts failed")
    return result


def main():
    parser = argparse.ArgumentParser(description="Download models from HuggingFace with mirror fallback")
    parser.add_argument("--repo-id", required=True, help="HuggingFace repo ID")
    parser.add_argument("--proxy", default=None, help="Proxy URL")
    parser.add_argument("--hf-token", default=None, help="HuggingFace token")
    parser.add_argument("--timeout", type=int, default=300, help="Download timeout in seconds")
    
    args = parser.parse_args()
    
    result = download_with_fallback(
        repo_id=args.repo_id,
        proxy=args.proxy,
        hf_token=args.hf_token,
        timeout=args.timeout
    )
    
    if result["success"]:
        print(f"\n✅ Model downloaded successfully from {result['source']}")
        sys.exit(0)
    else:
        print(f"\n❌ Failed to download model after {result['attempts']} attempts")
        sys.exit(1)


if __name__ == "__main__":
    main()
