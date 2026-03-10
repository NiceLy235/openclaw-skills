#!/usr/bin/env python3
"""
Check detailed GPU status and availability on remote nodes.

Usage:
    python check_gpu_status.py --ip 192.168.136.168 [--ssh-user username]
    python check_gpu_status.py --all [--subnet 192.168.136.0/24]
"""

import argparse
import subprocess
import json
from typing import Dict, List, Optional


def check_gpu_detailed(ip: str, ssh_user: str = None, timeout: int = 10) -> Optional[Dict]:
    """
    Get detailed GPU status from remote node.
    Returns comprehensive GPU info including memory, processes, and availability.
    """
    ssh_cmd = ['ssh']
    if ssh_user:
        ssh_cmd.extend([f'{ssh_user}@{ip}'])
    else:
        ssh_cmd.append(ip)
    
    # Get full GPU info
    ssh_cmd.extend([
        'nvidia-smi',
        '--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu,utilization.memory,temperature.gpu',
        '--format=csv,noheader,nounits'
    ])
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            return None
        
        gpus = []
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 8:
                gpu = {
                    'index': int(parts[0]),
                    'name': parts[1],
                    'memory_total_mb': int(parts[2]),
                    'memory_used_mb': int(parts[3]),
                    'memory_free_mb': int(parts[4]),
                    'gpu_utilization': int(parts[5]),
                    'memory_utilization': int(parts[6]),
                    'temperature_c': int(parts[7])
                }
                gpu['memory_used_pct'] = round(
                    (gpu['memory_used_mb'] / gpu['memory_total_mb']) * 100, 1
                )
                gpu['is_idle'] = (
                    gpu['gpu_utilization'] < 10 and 
                    gpu['memory_used_pct'] < 20
                )
                gpus.append(gpu)
        
        # Check running processes
        process_cmd = ssh_cmd[:-1] + [
            'nvidia-smi',
            '--query-compute-apps=pid,name,used_memory',
            '--format=csv,noheader'
        ]
        
        proc_result = subprocess.run(
            process_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        processes = []
        if proc_result.returncode == 0 and proc_result.stdout:
            for line in proc_result.stdout.strip().split('\n'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    processes.append({
                        'pid': parts[0],
                        'name': parts[1],
                        'memory_mb': parts[2]
                    })
        
        return {
            'ip': ip,
            'gpus': gpus,
            'gpu_count': len(gpus),
            'processes': processes,
            'is_available': all(g['is_idle'] for g in gpus) and len(processes) == 0
        }
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError, IndexError):
        return None


def check_system_info(ip: str, ssh_user: str = None, timeout: int = 10) -> Optional[Dict]:
    """Get system information (CPU, RAM, disk)."""
    ssh_cmd = ['ssh']
    if ssh_user:
        ssh_cmd.extend([f'{ssh_user}@{ip}'])
    else:
        ssh_cmd.append(ip)
    
    # Get CPU and RAM info
    ssh_cmd.extend([
        'echo "CPU: $(nproc) cores"; '
        'free -h | awk \'/^Mem:/ {print "RAM: "$2" total, "$4" available"}\'; '
        'df -h ~ | tail -1 | awk \'{print "Disk: "$2" total, "$4" available"}\''
    ])
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            return {'ip': ip, 'system_info': result.stdout.strip()}
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    
    return None


def format_status_report(status: Dict) -> str:
    """Format GPU status for display."""
    lines = [f"{'='*60}"]
    lines.append(f"📍 Node: {status['ip']}")
    lines.append(f"{'='*60}")
    
    # Overall status
    status_icon = "✅" if status['is_available'] else "⚠️"
    lines.append(f"{status_icon} Status: {'AVAILABLE' if status['is_available'] else 'BUSY'}")
    lines.append(f"GPU Count: {status['gpu_count']}")
    
    # GPU details
    for gpu in status['gpus']:
        lines.append(f"\n🎮 GPU {gpu['index']}: {gpu['name']}")
        lines.append(f"   Memory: {gpu['memory_used_mb']}/{gpu['memory_total_mb']} MB ({gpu['memory_used_pct']}%)")
        lines.append(f"   GPU Util: {gpu['gpu_utilization']}% | Memory Util: {gpu['memory_utilization']}%")
        lines.append(f"   Temperature: {gpu['temperature_c']}°C")
        
        if gpu['is_idle']:
            lines.append(f"   ✓ IDLE (ready for training)")
        else:
            lines.append(f"   ⚠️ BUSY (utilization > 10% or memory > 20%)")
    
    # Running processes
    if status['processes']:
        lines.append(f"\n⚠️ Running GPU processes:")
        for proc in status['processes']:
            lines.append(f"   - PID {proc['pid']}: {proc['name']} ({proc['memory_mb']})")
    else:
        lines.append(f"\n✅ No GPU processes running")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Check GPU status on remote nodes')
    parser.add_argument('--ip', help='Specific IP to check')
    parser.add_argument('--all', action='store_true', help='Check all nodes in subnet')
    parser.add_argument('--subnet', default='192.168.136.0/24', help='Subnet to scan')
    parser.add_argument('--ssh-user', help='SSH username')
    parser.add_argument('--timeout', type=int, default=10, help='SSH timeout')
    parser.add_argument('--output', choices=['text', 'json'], default='text')
    
    args = parser.parse_args()
    
    if args.ip:
        # Check single node
        status = check_gpu_detailed(args.ip, args.ssh_user, args.timeout)
        if status:
            if args.output == 'json':
                print(json.dumps(status, indent=2))
            else:
                print(format_status_report(status))
        else:
            print(f"❌ Failed to check {args.ip}")
    elif args.all:
        # Scan all nodes (would need to import scan_gpu_nodes)
        print("Use scan_gpu_nodes.py for bulk scanning")
    else:
        parser.error("Please specify --ip or --all")


if __name__ == '__main__':
    main()
