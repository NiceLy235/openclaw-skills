#!/usr/bin/env python3
"""
Deploy training script to remote GPU node and start training.

Usage:
    python deploy_and_train.py --ip 192.168.136.168 --config config.json [--ssh-user username]
"""

import argparse
import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, Optional


def generate_training_command(config: Dict) -> str:
    """Generate lerobot-train command from config."""
    cmd_parts = ['lerobot-train']
    
    # Required parameters
    cmd_parts.append(f"--policy.pretrained_path={config.get('pretrained_path', 'lerobot/smolvla_base')}")
    cmd_parts.append(f"--policy.type={config.get('policy_type', 'smolvla')}")
    cmd_parts.append(f"--policy.load_vlm_weights={config.get('load_vlm_weights', True)}")
    
    # Dataset
    cmd_parts.append(f"--dataset.repo_id={config['dataset']}")
    
    # Output
    cmd_parts.append(f"--output_dir={config.get('output_dir', 'outputs/train')}")
    cmd_parts.append(f"--job_name={config.get('job_name', 'train_job')}")
    
    # Training parameters
    cmd_parts.append("--policy.device=cuda")
    cmd_parts.append(f"--wandb.enable={config.get('wandb_enable', False)}")
    cmd_parts.append(f"--batch_size={config.get('batch_size', 32)}")
    cmd_parts.append(f"--steps={config.get('steps', 200000)}")
    cmd_parts.append(f"--save_freq={config.get('save_freq', 10000)}")
    cmd_parts.append(f"--eval_freq={config.get('eval_freq', -1)}")
    cmd_parts.append(f"--num_workers={config.get('num_workers', 16)}")
    
    # Optional parameters
    if config.get('policy_repo_id'):
        cmd_parts.append(f"--policy.repo_id={config['policy_repo_id']}")
    
    cmd_parts.append(f"--policy.push_to_hub={config.get('push_to_hub', False)}")
    cmd_parts.append(f"--policy.train_expert_only={config.get('train_expert_only', False)}")
    
    return ' \\\n  '.join(cmd_parts)


def check_prerequisites(ip: str, ssh_user: str = None, timeout: int = 10) -> bool:
    """Check if remote node has required software."""
    ssh_cmd = ['ssh']
    if ssh_user:
        ssh_cmd.append(f'{ssh_user}@{ip}')
    else:
        ssh_cmd.append(ip)
    
    # Check lerobot installation
    ssh_cmd.append('which lerobot-train')
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, timeout=timeout)
        if result.returncode == 0:
            print(f"✅ lerobot-train found on {ip}")
            return True
        else:
            print(f"❌ lerobot-train not found on {ip}")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        print(f"❌ Failed to check {ip}")
        return False


def deploy_and_start_training(ip: str, 
                             config: Dict,
                             ssh_user: str = None,
                             run_in_background: bool = True,
                             log_file: str = None) -> Optional[str]:
    """
    Deploy and start training on remote node.
    
    Returns:
        Process ID if successful, None otherwise
    """
    # Check prerequisites
    if not check_prerequisites(ip, ssh_user):
        return None
    
    # Generate command
    training_cmd = generate_training_command(config)
    print(f"\n📝 Generated training command:")
    print(training_cmd)
    print()
    
    # Prepare SSH command
    ssh_cmd = ['ssh']
    if ssh_user:
        ssh_cmd.append(f'{ssh_user}@{ip}')
    else:
        ssh_cmd.append(ip)
    
    # Build remote command
    if run_in_background:
        if not log_file:
            log_file = f"training_{config.get('job_name', 'job')}_{ip.replace('.', '_')}.log"
        
        # Run in background with nohup
        remote_cmd = f'nohup bash -c "{training_cmd}" > {log_file} 2>&1 & echo $!'
        ssh_cmd.append(remote_cmd)
    else:
        ssh_cmd.append(training_cmd)
    
    print(f"🚀 Starting training on {ip}...")
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            if run_in_background:
                pid = result.stdout.strip()
                print(f"✅ Training started! PID: {pid}")
                print(f"📄 Log file: {log_file}")
                print(f"\n💡 Monitor with:")
                print(f"   ssh {ssh_user + '@' if ssh_user else ''}{ip} 'tail -f {log_file}'")
                return pid
            else:
                print("✅ Training started in foreground")
                return "foreground"
        else:
            print(f"❌ Failed to start training:")
            print(result.stderr)
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ SSH connection timeout")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Deploy and start training on remote GPU node')
    parser.add_argument('--ip', required=True, help='Remote node IP')
    parser.add_argument('--config', required=True, help='Training config JSON file')
    parser.add_argument('--ssh-user', help='SSH username')
    parser.add_argument('--foreground', action='store_true', help='Run in foreground')
    parser.add_argument('--log-file', help='Log file path on remote node')
    parser.add_argument('--dry-run', action='store_true', help='Just print command, don\'t execute')
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    if args.dry_run:
        print("Dry run - generated command:")
        print(generate_training_command(config))
    else:
        pid = deploy_and_start_training(
            ip=args.ip,
            config=config,
            ssh_user=args.ssh_user,
            run_in_background=not args.foreground,
            log_file=args.log_file
        )
        
        if pid:
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == '__main__':
    main()
