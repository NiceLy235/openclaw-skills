#!/usr/bin/env python3
"""
Manage training memory and experiences.

Usage:
    python memory_manager.py record --user-ip 192.168.136.168 --config config.json --issue "OOM error" --solution "Reduce batch size"
    python memory_manager.py query --user-ip 192.168.136.168
    python memory_manager.py upload --repo user/training-memories --token $GITHUB_TOKEN
"""

import argparse
import json
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class TrainingMemoryManager:
    def __init__(self, memory_dir: str = None):
        """Initialize memory manager."""
        if memory_dir is None:
            memory_dir = os.path.expanduser("~/.lerobot_training_memory")
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.current_user_file = self.memory_dir / "current_user.json"
    
    def get_user_id(self, ip: str) -> str:
        """Get or create user ID based on IP."""
        if self.current_user_file.exists():
            with open(self.current_user_file, 'r') as f:
                users = json.load(f)
        else:
            users = {}
        
        if ip not in users:
            users[ip] = {
                'user_id': f"user_{len(users) + 1}",
                'first_seen': datetime.now().isoformat(),
                'training_count': 0
            }
        
        users[ip]['last_seen'] = datetime.now().isoformat()
        
        with open(self.current_user_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        return users[ip]['user_id']
    
    def record_experience(self, 
                         user_ip: str,
                         config: Dict,
                         issue: Optional[str] = None,
                         solution: Optional[str] = None,
                         status: str = "success",
                         notes: Optional[str] = None) -> Dict:
        """
        Record a training experience.
        
        Args:
            user_ip: User's IP address
            config: Training configuration
            issue: Problem encountered (if any)
            solution: How the problem was solved
            status: "success", "failed", "resolved"
            notes: Additional notes
        
        Returns:
            Recorded experience dict
        """
        user_id = self.get_user_id(user_ip)
        timestamp = datetime.now()
        
        experience = {
            'timestamp': timestamp.isoformat(),
            'user_id': user_id,
            'user_ip': user_ip,
            'config': config,
            'issue': issue,
            'solution': solution,
            'status': status,
            'notes': notes,
            'gpu_info': config.get('gpu_info', 'unknown')
        }
        
        # Save to daily memory file
        memory_file = self.memory_dir / f"memory_{timestamp.strftime('%Y-%m-%d')}.json"
        
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                memories = json.load(f)
        else:
            memories = []
        
        memories.append(experience)
        
        with open(memory_file, 'w') as f:
            json.dump(memories, f, indent=2)
        
        print(f"✅ Recorded experience for {user_id}")
        
        # Update user training count
        with open(self.current_user_file, 'r') as f:
            users = json.load(f)
        users[user_ip]['training_count'] += 1
        with open(self.current_user_file, 'w') as f:
            json.dump(users, f, indent=2)
        
        return experience
    
    def query_experiences(self, 
                         user_ip: Optional[str] = None,
                         limit: int = 10,
                         status: Optional[str] = None) -> List[Dict]:
        """
        Query training experiences.
        
        Args:
            user_ip: Filter by user IP
            limit: Maximum number of results
            status: Filter by status
        
        Returns:
            List of experiences
        """
        experiences = []
        
        # Read all memory files
        for memory_file in sorted(self.memory_dir.glob("memory_*.json"), reverse=True):
            with open(memory_file, 'r') as f:
                daily_memories = json.load(f)
                experiences.extend(daily_memories)
        
        # Filter
        if user_ip:
            experiences = [e for e in experiences if e['user_ip'] == user_ip]
        
        if status:
            experiences = [e for e in experiences if e['status'] == status]
        
        # Sort by timestamp and limit
        experiences = sorted(experiences, key=lambda x: x['timestamp'], reverse=True)
        
        return experiences[:limit]
    
    def get_common_issues(self) -> List[Dict]:
        """Get most common issues and their solutions."""
        experiences = self.query_experiences(limit=1000)
        
        issues = {}
        for exp in experiences:
            if exp['issue']:
                key = exp['issue']
                if key not in issues:
                    issues[key] = {
                        'issue': key,
                        'count': 0,
                        'solutions': set(),
                        'successful_configs': []
                    }
                
                issues[key]['count'] += 1
                
                if exp['solution']:
                    issues[key]['solutions'].add(exp['solution'])
                
                if exp['status'] == 'success' and exp['config']:
                    issues[key]['successful_configs'].append(exp['config'])
        
        # Sort by frequency
        common = sorted(issues.values(), key=lambda x: x['count'], reverse=True)
        
        # Convert sets to lists for JSON serialization
        for issue in common:
            issue['solutions'] = list(issue['solutions'])
        
        return common
    
    def upload_to_github(self, repo: str, token: str, branch: str = "main") -> bool:
        """
        Upload memory files to GitHub repository.
        
        Args:
            repo: Repository in format "user/repo"
            token: GitHub personal access token
            branch: Branch name
        
        Returns:
            Success status
        """
        try:
            # Configure git
            subprocess.run(['git', 'config', '--global', 'user.email', 'training-bot@example.com'], check=True)
            subprocess.run(['git', 'config', '--global', 'user.name', 'Training Memory Bot'], check=True)
            
            # Clone or update repo
            repo_url = f"https://{token}@github.com/{repo}.git"
            repo_dir = self.memory_dir / "github_repo"
            
            if repo_dir.exists():
                subprocess.run(['git', 'pull'], cwd=repo_dir, check=True)
            else:
                subprocess.run(['git', 'clone', repo_url, str(repo_dir)], check=True)
            
            # Copy memory files
            memory_subdir = repo_dir / "training_memories"
            memory_subdir.mkdir(exist_ok=True)
            
            for memory_file in self.memory_dir.glob("memory_*.json"):
                dest = memory_subdir / memory_file.name
                dest.write_text(memory_file.read_text())
            
            # Copy user file
            user_dest = memory_subdir / "current_user.json"
            user_dest.write_text(self.current_user_file.read_text())
            
            # Commit and push
            subprocess.run(['git', 'add', '.'], cwd=repo_dir, check=True)
            subprocess.run(['git', 'commit', '-m', f'Update training memories {datetime.now().isoformat()}'], 
                          cwd=repo_dir, check=True)
            subprocess.run(['git', 'push', 'origin', branch], cwd=repo_dir, check=True)
            
            print(f"✅ Uploaded memories to {repo}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to upload to GitHub: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Manage training memories')
    parser.add_argument('--memory-dir', help='Memory directory path')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Record command
    record_parser = subparsers.add_parser('record', help='Record a training experience')
    record_parser.add_argument('--user-ip', required=True, help='User IP address')
    record_parser.add_argument('--config', required=True, help='Training config JSON file')
    record_parser.add_argument('--issue', help='Problem encountered')
    record_parser.add_argument('--solution', help='Solution applied')
    record_parser.add_argument('--status', default='success', choices=['success', 'failed', 'resolved'])
    record_parser.add_argument('--notes', help='Additional notes')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query training experiences')
    query_parser.add_argument('--user-ip', help='Filter by user IP')
    query_parser.add_argument('--limit', type=int, default=10, help='Max results')
    query_parser.add_argument('--status', help='Filter by status')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload memories to GitHub')
    upload_parser.add_argument('--repo', required=True, help='GitHub repo (user/repo)')
    upload_parser.add_argument('--token', required=True, help='GitHub token')
    upload_parser.add_argument('--branch', default='main', help='Branch name')
    
    # Common issues command
    issues_parser = subparsers.add_parser('issues', help='Get common issues')
    
    args = parser.parse_args()
    
    manager = TrainingMemoryManager(args.memory_dir)
    
    if args.command == 'record':
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        exp = manager.record_experience(
            user_ip=args.user_ip,
            config=config,
            issue=args.issue,
            solution=args.solution,
            status=args.status,
            notes=args.notes
        )
        print(json.dumps(exp, indent=2))
    
    elif args.command == 'query':
        experiences = manager.query_experiences(
            user_ip=args.user_ip,
            limit=args.limit,
            status=args.status
        )
        print(json.dumps(experiences, indent=2))
    
    elif args.command == 'upload':
        success = manager.upload_to_github(args.repo, args.token, args.branch)
        print("Upload successful" if success else "Upload failed")
    
    elif args.command == 'issues':
        issues = manager.get_common_issues()
        print(json.dumps(issues, indent=2))


if __name__ == '__main__':
    main()
