#!/usr/bin/env python3
"""
Scan LAN for GPU nodes with SSH access.

Usage:
    python scan_gpu_nodes.py [--subnet 192.168.136.0/24] [--timeout 2]
"""

import argparse
import subprocess
import ipaddress
import concurrent.futures
import json
from typing import List, Dict, Optional


def check_ssh_connection(ip: str, timeout: int = 2) -> bool:
    """Check if SSH port is open on the given IP."""
    try:
        result = subprocess.run(
            ['nc', '-z', '-w', str(timeout), ip, '22'],
            capture_output=True,
            timeout=timeout + 1
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_nvidia_gpu(ip: str, ssh_user: str = None, timeout: int = 5) -> Optional[Dict]:
    """
    Check if remote host has NVIDIA GPU via SSH.
    Returns GPU info dict or None.
    """
    ssh_cmd = ['ssh']
    if ssh_user:
        ssh_cmd.extend([f'{ssh_user}@{ip}'])
    else:
        ssh_cmd.append(ip)
    
    # Check nvidia-smi
    ssh_cmd.extend([
        'nvidia-smi',
        '--query-gpu=name,memory.total,utilization.gpu',
        '--format=csv,noheader,nounits'
    ])
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0 and result.stdout:
            # Parse GPU info
            lines = result.stdout.strip().split('\n')
            gpus = []
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    gpus.append({
                        'name': parts[0],
                        'memory_mb': int(parts[1]),
                        'utilization': int(parts[2])
                    })
            
            if gpus:
                return {
                    'ip': ip,
                    'gpus': gpus,
                    'gpu_count': len(gpus)
                }
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
        pass
    
    return None


def scan_subnet(subnet: str, timeout: int = 2, max_workers: int = 50) -> List[str]:
    """Scan subnet for active hosts with SSH."""
    network = ipaddress.ip_network(subnet, strict=False)
    active_hosts = []
    
    print(f"🔍 Scanning {subnet} for SSH-accessible hosts...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_ssh_connection, str(ip), timeout): ip 
                   for ip in network.hosts()}
        
        for future in concurrent.futures.as_completed(futures):
            ip = futures[future]
            try:
                if future.result():
                    active_hosts.append(str(ip))
            except Exception:
                pass
    
    return active_hosts


def scan_gpu_nodes(subnet: str = '192.168.136.0/24', 
                   ssh_user: str = None,
                   timeout: int = 2) -> List[Dict]:
    """
    Scan subnet for GPU nodes.
    Returns list of GPU node info dicts.
    """
    # Step 1: Find SSH-accessible hosts
    active_hosts = scan_subnet(subnet, timeout)
    print(f"✅ Found {len(active_hosts)} SSH-accessible hosts")
    
    # Step 2: Check each host for GPU
    gpu_nodes = []
    print("🔍 Checking for NVIDIA GPUs...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_nvidia_gpu, ip, ssh_user, timeout * 3): ip 
                   for ip in active_hosts}
        
        for future in concurrent.futures.as_completed(futures):
            ip = futures[future]
            try:
                gpu_info = future.result()
                if gpu_info:
                    gpu_nodes.append(gpu_info)
                    print(f"  ✓ {ip}: {gpu_info['gpu_count']} GPU(s)")
            except Exception:
                pass
    
    return gpu_nodes


def main():
    parser = argparse.ArgumentParser(description='Scan LAN for GPU nodes')
    parser.add_argument('--subnet', default='192.168.136.0/24',
                       help='Subnet to scan (default: 192.168.136.0/24)')
    parser.add_argument('--ssh-user', help='SSH username')
    parser.add_argument('--timeout', type=int, default=2,
                       help='Connection timeout in seconds')
    parser.add_argument('--output', choices=['text', 'json'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    gpu_nodes = scan_gpu_nodes(args.subnet, args.ssh_user, args.timeout)
    
    if args.output == 'json':
        print(json.dumps(gpu_nodes, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"GPU Nodes Found: {len(gpu_nodes)}")
        print(f"{'='*60}")
        
        for node in gpu_nodes:
            print(f"\n📍 {node['ip']} ({node['gpu_count']} GPU(s))")
            for gpu in node['gpus']:
                print(f"   - {gpu['name']}")
                print(f"     Memory: {gpu['memory_mb']} MB")
                print(f"     Utilization: {gpu['utilization']}%")


if __name__ == '__main__':
    main()
