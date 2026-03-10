#!/usr/bin/env python3
"""
Monitor training progress on remote GPU nodes.

Usage:
    python monitor_training.py --ip 192.168.136.168 --log-file training.log [--ssh-user username]
    python monitor_training.py --ip 192.168.136.168 --pid 12345 [--ssh-user username]
"""

import argparse
import subprocess
import time
import re
from typing import Optional, Dict
from pathlib import Path


def tail_remote_log(ip: str, 
                    log_file: str,
                    ssh_user: str = None,
                    lines: int = 50,
                    follow: bool = True) -> None:
    """Tail remote log file."""
    ssh_cmd = ['ssh']
    if ssh_user:
        ssh_cmd.append(f'{ssh_user}@{ip}')
    else:
        ssh_cmd.append(ip)
    
    if follow:
        ssh_cmd.append(f'tail -f -n {lines} {log_file}')
    else:
        ssh_cmd.append(f'tail -n {lines} {log_file}')
    
    try:
        subprocess.run(ssh_cmd)
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")


def check_process_status(ip: str, pid: str, ssh_user: str = None) -> Optional[Dict]:
    """Check if training process is still running."""
    ssh_cmd = ['ssh']
    if ssh_user:
        ssh_cmd.append(f'{ssh_user}@{ip}')
    else:
        ssh_cmd.append(ip)
    
    ssh_cmd.extend([
        'ps',
        '-p', pid,
        '-o', 'pid,ppid,cmd,%cpu,%mem,etime',
        '--no-headers'
    ])
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            parts = result.stdout.strip().split(None, 5)
            return {
                'pid': parts[0],
                'ppid': parts[1],
                'cmd': parts[2] if len(parts) > 2 else 'unknown',
                'cpu_pct': parts[3] if len(parts) > 3 else '0',
                'mem_pct': parts[4] if len(parts) > 4 else '0',
                'elapsed': parts[5] if len(parts) > 5 else 'unknown',
                'is_running': True
            }
        else:
            return {'pid': pid, 'is_running': False}
    
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return None


def parse_training_metrics(log_content: str) -> Dict:
    """Parse training metrics from log content."""
    metrics = {
        'current_step': 0,
        'total_steps': 0,
        'loss': None,
        'lr': None,
        'epoch': None,
        'last_update': None
    }
    
    # Look for common training log patterns
    # Example: "Step 1000/200000 | Loss: 0.123 | LR: 0.001"
    
    step_pattern = r'Step[:\s]+(\d+)/(\d+)'
    loss_pattern = r'Loss[:\s]+([\d.]+)'
    lr_pattern = r'LR[:\s]+([\d.e-]+)'
    epoch_pattern = r'Epoch[:\s]+([\d.]+)'
    
    lines = log_content.strip().split('\n')
    
    for line in reversed(lines[-100:]):  # Check last 100 lines
        step_match = re.search(step_pattern, line)
        if step_match:
            metrics['current_step'] = int(step_match.group(1))
            metrics['total_steps'] = int(step_match.group(2))
        
        loss_match = re.search(loss_pattern, line)
        if loss_match:
            metrics['loss'] = float(loss_match.group(1))
        
        lr_match = re.search(lr_pattern, line)
        if lr_match:
            metrics['lr'] = float(lr_match.group(1))
        
        epoch_match = re.search(epoch_pattern, line)
        if epoch_match:
            metrics['epoch'] = float(epoch_match.group(1))
    
    return metrics


def monitor_with_gpu(ip: str, 
                     pid: str,
                     ssh_user: str = None,
                     interval: int = 10) -> None:
    """Monitor training process with GPU metrics."""
    print(f"🔍 Monitoring training on {ip} (PID: {pid})")
    print(f"{'='*60}")
    
    try:
        while True:
            # Check process status
            status = check_process_status(ip, pid, ssh_user)
            
            if not status:
                print("❌ Failed to check process status")
                break
            
            if not status['is_running']:
                print(f"⏹️ Process {pid} has stopped")
                break
            
            # Get GPU status
            gpu_cmd = ['ssh']
            if ssh_user:
                gpu_cmd.append(f'{ssh_user}@{ip}')
            else:
                gpu_cmd.append(ip)
            
            gpu_cmd.extend([
                'nvidia-smi',
                '--query-gpu=utilization.gpu,memory.used,memory.total',
                '--format=csv,noheader,nounits'
            ])
            
            gpu_result = subprocess.run(gpu_cmd, capture_output=True, text=True, timeout=10)
            
            timestamp = time.strftime('%H:%M:%S')
            
            print(f"\n[{timestamp}] Step: Running | CPU: {status['cpu_pct']}% | MEM: {status['mem_pct']}%")
            
            if gpu_result.returncode == 0:
                gpu_parts = gpu_result.stdout.strip().split(', ')
                if len(gpu_parts) >= 3:
                    print(f"          GPU Util: {gpu_parts[0]}% | VRAM: {gpu_parts[1]}/{gpu_parts[2]} MB")
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")


def main():
    parser = argparse.ArgumentParser(description='Monitor training progress')
    parser.add_argument('--ip', required=True, help='Remote node IP')
    parser.add_argument('--ssh-user', help='SSH username')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--log-file', help='Log file to tail')
    group.add_argument('--pid', help='Process ID to monitor')
    
    parser.add_argument('--lines', type=int, default=50, help='Number of lines to show')
    parser.add_argument('--no-follow', action='store_true', help='Don\'t follow log')
    parser.add_argument('--interval', type=int, default=10, help='Monitor interval (seconds)')
    
    args = parser.parse_args()
    
    if args.log_file:
        tail_remote_log(
            ip=args.ip,
            log_file=args.log_file,
            ssh_user=args.ssh_user,
            lines=args.lines,
            follow=not args.no_follow
        )
    elif args.pid:
        monitor_with_gpu(
            ip=args.ip,
            pid=args.pid,
            ssh_user=args.ssh_user,
            interval=args.interval
        )


if __name__ == '__main__':
    main()
