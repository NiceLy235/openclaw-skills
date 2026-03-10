---
name: github-sync
description: >
  Automatically sync OpenClaw memories and skills to GitHub repositories.
  Handles both daily memory sync and skill updates with proxy support.
  
  Features:
  - Daily memory sync to training-memories repo
  - Skill sync to skills repo
  - Automatic V2Ray proxy configuration
  - Conflict resolution and error recovery
  - Configurable sync schedules
  
  Use when: (1) Setting up automatic GitHub sync, (2) Pushing skills to GitHub,
  (3) Configuring daily memory sync, (4) Managing multiple GitHub repositories,
  (5) User mentions 'sync to github', 'push skills', 'automatic backup'.
---

# GitHub Sync Skill

Automatically sync OpenClaw content to multiple GitHub repositories.

## 🎯 Key Features

### 📚 Multi-Repository Support
- ✅ **Memory Repository**: Daily conversations, summaries, experiences
- ✅ **Skills Repository**: All custom skills and tools
- ✅ **Workspace Repository**: Complete workspace backup

### 🌐 Smart Proxy Configuration
- ✅ Auto-detect V2Ray (SOCKS5/HTTP)
- ✅ Configure Git to use proxy
- ✅ Test connectivity before sync

### ⏰ Flexible Scheduling
- ✅ Daily memory sync (23:00)
- ✅ Skill sync on changes
- ✅ Manual sync on demand

### 🔧 Conflict Resolution
- ✅ Auto-merge when possible
- ✅ Preserve local changes
- ✅ Detailed sync reports

## 📦 Repository Configuration

### Memory Repository
Stores daily memories and experiences:
```
https://github.com/NiceLy235/training-memories
├── conversations/
├── daily/
├── experiences/
└── errors/
```

### Skills Repository
Stores all OpenClaw skills:
```
https://github.com/USERNAME/openclaw-skills
├── skills/
│   ├── env-setup/
│   ├── lerobot-auto-train/
│   └── github-sync/
├── daily_summary/
└── scripts/
```

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Run setup script
cd ~/.openclaw/workspace/skills/github-sync/scripts
./setup_repos.sh
```

This will:
- ✅ Detect V2Ray proxy
- ✅ Configure Git remotes
- ✅ Test GitHub connectivity
- ✅ Set up cron jobs

### 2. Configure Repositories

Edit `config.json`:
```json
{
  "repositories": {
    "memory": {
      "url": "https://github.com/NiceLy235/training-memories.git",
      "branch": "main",
      "sync_enabled": true,
      "schedule": "daily"
    },
    "skills": {
      "url": "https://github.com/USERNAME/openclaw-skills.git",
      "branch": "main",
      "sync_enabled": true,
      "schedule": "on_change"
    }
  },
  "proxy": {
    "enabled": true,
    "http": "http://127.0.0.1:10809",
    "socks5": "socks5://127.0.0.1:10808"
  },
  "schedule": {
    "memory_sync": "23:00",
    "skills_sync": "on_demand"
  }
}
```

### 3. Manual Sync

```bash
# Sync memory only
./sync_memory.sh

# Sync skills only
./sync_skills.sh

# Sync everything
./sync_all.sh
```

### 4. Check Status

```bash
./sync_status.sh
```

## 📅 Automatic Scheduling

### Daily Memory Sync
Runs every day at 23:00:
```bash
0 23 * * * /root/.openclaw/workspace/skills/github-sync/scripts/sync_memory.sh
```

### Skills Sync
Runs when skills are updated:
```bash
# Automatically triggered by file watcher
# or manual: ./sync_skills.sh
```

## 🔧 Sync Workflow

### Memory Sync Process
```
1. Generate daily summary
   ↓
2. Extract experiences
   ↓
3. Check for changes
   ↓
4. Configure proxy
   ↓
5. Commit changes
   ↓
6. Push to GitHub
   ↓
7. Generate report
```

### Skills Sync Process
```
1. Detect changed skills
   ↓
2. Validate skill structure
   ↓
3. Configure proxy
   ↓
4. Commit changes
   ↓
5. Push to GitHub
   ↓
6. Update sync log
```

## 📊 Sync Reports

After each sync, a report is generated:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GitHub Sync Report - 2026-03-10 23:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Memory Sync:
  ✅ Conversations: 3 new files
  ✅ Daily summaries: 1 new file
  ✅ Experiences: 1 new file
  ✅ Pushed to: NiceLy235/training-memories

📚 Skills Sync:
  ✅ env-setup: 5 files changed
  ✅ lerobot-auto-train: 3 files changed
  ✅ Pushed to: USERNAME/openclaw-skills

⏱️  Duration: 15 seconds
🌐 Proxy: V2Ray (127.0.0.1:10809)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🚨 Error Handling

### Network Issues
```bash
# Test connectivity
curl -x http://127.0.0.1:10809 -I https://github.com

# Restart V2Ray
sudo systemctl restart v2ray
```

### Merge Conflicts
```bash
# View conflicts
./sync_status.sh --conflicts

# Resolve and retry
./sync_all.sh --force
```

### Authentication Errors
```bash
# Update credentials
git config --local credential.helper store
./setup_repos.sh --update-credentials
```

## 🔍 Status Commands

```bash
# Check sync status
./sync_status.sh

# View sync history
tail -100 ~/.openclaw/github_sync.log

# Check repository status
./sync_status.sh --repos

# Check next scheduled sync
./sync_status.sh --schedule
```

## 📝 Configuration

### Enable/Disable Sync

```bash
# Disable memory sync
./config.sh --disable memory

# Enable skills sync
./config.sh --enable skills

# Disable all sync
./config.sh --disable all
```

### Change Schedule

```bash
# Change memory sync to 22:00
./config.sh --schedule memory 22:00

# Enable automatic skills sync every 6 hours
./config.sh --schedule skills "0 */6 * * *"
```

## 🔄 Manual Operations

### Update and Sync Skill (One Command)

```bash
# Update skill and auto-sync to GitHub
./update_skill.sh <skill_name> "commit message"

# Example
./update_skill.sh env-setup "Add Python 3.12 support"
```

This will:
1. ✅ Commit skill changes
2. ✅ Sync to GitHub immediately
3. ✅ Send real-time progress updates

### Force Push

```bash
# Force push to memory repo
./sync_memory.sh --force

# Force push to skills repo
./sync_skills.sh --force
```

### Dry Run

```bash
# See what would be synced
./sync_all.sh --dry-run
```

### Rollback

```bash
# Rollback last sync
./sync_rollback.sh --last

# Rollback to specific date
./sync_rollback.sh --date 2026-03-09
```

## 📚 Related Documentation

- [Setup Guide](references/setup_guide.md)
- [Troubleshooting](references/troubleshooting.md)
- [API Reference](references/api_reference.md)

## 🎯 Best Practices

1. **Check V2Ray before sync**:
   ```bash
   systemctl status v2ray
   ```

2. **Review changes before sync**:
   ```bash
   git status
   git diff
   ```

3. **Regular backups**:
   ```bash
   # Create backup before major changes
   ./backup.sh --full
   ```

4. **Monitor sync logs**:
   ```bash
   tail -f ~/.openclaw/github_sync.log
   ```

5. **After updating ANY skill, sync to GitHub**:
   ```bash
   # One command to update and sync
   ./update_skill.sh <skill_name> "your commit message"
   
   # Or manual steps:
   git add skills/YOUR_SKILL/
   git commit -m "feat: Your changes"
   ./sync_skills.sh
   ```

## 🚀 Advanced Usage

### Sync Specific Skills

```bash
# Sync only env-setup skill
./sync_skills.sh --skill env-setup

# Sync multiple skills
./sync_skills.sh --skill env-setup,lerobot-auto-train
```

### Custom Sync Hooks

Create `~/.openclaw/sync_hooks.sh`:
```bash
#!/bin/bash
# Pre-sync hook
pre_sync() {
    echo "Running pre-sync tasks..."
    # Add custom tasks
}

# Post-sync hook
post_sync() {
    echo "Running post-sync tasks..."
    # Add custom tasks
}
```

### Sync to Multiple Remotes

```bash
# Add additional remote
git remote add backup https://github.com/BACKUP/repo.git

# Sync to all remotes
./sync_all.sh --all-remotes
```

## 🔐 Security

### SSH Keys (Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub
cat ~/.ssh/id_ed25519.pub
# Copy to GitHub Settings > SSH Keys

# Test
ssh -T git@github.com
```

### HTTPS with Token

```bash
# Create token
# https://github.com/settings/tokens

# Configure
git remote set-url origin https://TOKEN@github.com/USER/REPO.git
```

## 📞 Support

### Logs Location
- Sync log: `~/.openclaw/github_sync.log`
- Error log: `~/.openclaw/github_sync_errors.log`
- Config: `~/.openclaw/workspace/skills/github-sync/config.json`

### Quick Diagnostics
```bash
./diagnose.sh
```

### Community
- GitHub Issues: [Report bugs]
- Discord: https://discord.gg/clawd
