---
name: github-sync
description: >
  Automatically sync OpenClaw memories and skills to GitHub repositories.
  Handles both daily memory sync and skill updates with proxy support.

  Use when: (1) Setting up automatic GitHub sync, (2) Pushing skills to GitHub,
  (3) Configuring daily memory sync, (4) Managing multiple GitHub repositories,
  (5) User mentions 'sync to github', 'push skills', 'automatic backup'.

  MANDATORY: Execute steps in strict order. Stop on any error.
metadata:
  {
    "openclaw": {
      "emoji": "🔄"
    }
  }
---

# GitHub Sync Skill

Automatically sync OpenClaw content to multiple GitHub repositories.

⚠️ **CRITICAL: Execute steps in strict order as listed below. Do NOT skip any step.**

---

## MANDATORY Execution Rules

1. **Execute steps sequentially** - Complete Step 1 before starting Step 2
2. **Report progress after EACH step** - Inform user of completion before proceeding
3. **Do NOT skip verification steps** - Always run git status and connectivity checks
4. **Stop on error** - If any step fails, report the error and STOP. Do NOT proceed with remaining steps
5. **Verify connectivity before sync** - Test GitHub connectivity before any git operations
6. **Require user confirmation for destructive operations** - For force push or overwrite, ask user to confirm

---

## Progress Reporting Rules

1. **Start each step** with: `### Step X: [Name]`
2. **After each step**, report: `✅ Step X completed: [summary]`
3. **If a step fails**, report: `❌ Step X failed: [error details]`
4. **Before next step**, indicate: `→ Proceeding to Step X+1...`

---

## Step-by-Step Execution Template

Use this template for ANY sync operation:

### Step 1: Pre-flight Checks
- **Action**: Verify V2Ray proxy status and Git configuration
- **Command**:
  ```bash
  systemctl status v2ray --no-pager
  git config --list --show-origin | grep -E "(user|remote|proxy)"
  ```
- **Expected**: V2Ray running (active), Git remotes configured
**[Run command and report output]**

### Step 2: Test GitHub Connectivity
- **Action**: Test connection to GitHub via proxy
- **Command**:
  ```bash
  curl -x http://127.0.0.1:10809 -I https://github.com --connect-timeout 10
  ```
- **Expected**: HTTP 200 or 301 response from GitHub
**[Run command and report result]**

### Step 3: Check Repository Status
- **Action**: Check git status for uncommitted changes
- **Command**:
  ```bash
  cd /path/to/repo && git status --short
  ```
- **Expected**: List of modified/new files or "nothing to commit"
**[Run command and report]**

### Step 4: Generate Daily Summary (Memory Sync Only)
- **Action**: Generate summary of conversations and experiences
- **Command**:
  ```bash
  python scripts/generate_summary.py
  ```
- **Expected**: Summary files created (daily_summary_YYYYMMDD.txt, etc.)
**[Run command and verify files exist]**

### Step 5: Stage Changes
- **Action**: Stage all changes for commit
- **Command**:
  ```bash
  git add -A
  git status --short
  ```
- **Expected**: All changes staged (shown in git status)
**[Run command and report staged files]**

### Step 6: Commit Changes
- **Action**: Create commit with descriptive message
- **Command**:
  ```bash
  git commit -m "Auto-sync: $(date +%Y-%m-%d_%H%M%S)"
  ```
- **Expected**: Commit created with hash
**[Run command and report commit hash]**

### Step 7: Push to GitHub
- **Action**: Push changes to remote repository
- **Command**:
  ```bash
  export HTTPS_PROXY=http://127.0.0.1:10809
  git push origin main
  ```
- **Expected**: Push successful, remote updated
**[Run command and report result]**

### Step 8: Generate Sync Report
- **Action**: Create detailed sync report
- **Command**:
  ```bash
  python scripts/generate_report.py > /tmp/sync_report.txt
  cat /tmp/sync_report.txt
  ```
- **Expected**: Report file created with sync summary
**[Run command and display report]**

---

## Sync Types

### Memory Sync Workflow

Syncs daily conversations, summaries, and experiences to memory repository.

#### Prerequisites
- V2Ray proxy must be running
- Memory repository must be cloned
- Git credentials configured

#### Execution Steps

**### Step 1: Verify V2Ray Status**
- **Action**: Check if V2Ray is running
- **Command**: `systemctl status v2ray --no-pager | head -5`
- **Expected**: `Active: active (running)`
**[Run and report]**

**### Step 2: Test GitHub Connectivity**
- **Action**: Test connection to GitHub
- **Command**: `curl -x http://127.0.0.1:10809 -I https://github.com`
- **Expected**: HTTP 200/301 response
**[Run and report]**

**### Step 3: Generate Daily Summary**
- **Action**: Create summary of today's conversations
- **Command**:
  ```bash
  cd ~/.openclaw
  python workspace/skills/github-sync/scripts/generate_summary.py
  ```
- **Expected**: `daily_summary_*.txt` created
**[Run and verify]**

**### Step 4: Check for Changes**
- **Action**: Check git status in memory repo
- **Command**:
  ```bash
  cd ~/training-memories
  git status --short
  ```
- **Expected**: List of changed files or "nothing to commit"
**[Run and report]**

**### Step 5: Stage and Commit**
- **Action**: Stage and commit all changes
- **Command**:
  ```bash
  git add -A
  git commit -m "Auto-sync: $(date +%Y-%m-%d_%H%M%S)"
  ```
- **Expected**: Commit created with hash
**[Run and report commit hash]**

**### Step 6: Push to GitHub**
- **Action**: Push to remote repository
- **Command**:
  ```bash
  export HTTPS_PROXY=http://127.0.0.1:10809
  git push origin main
  ```
- **Expected**: Push successful
**[Run and report]**

**### Step 7: Generate Report**
- **Action**: Create sync report
- **Command**:
  ```bash
  echo "Memory Sync Report - $(date)" > /tmp/memory_sync.log
  git log -1 --oneline >> /tmp/memory_sync.log
  cat /tmp/memory_sync.log
  ```
- **Expected**: Report displayed
**[Run and display]**

---

### Skills Sync Workflow

Syncs updated skills to skills repository.

#### Prerequisites
- V2Ray proxy must be running
- Skills repository must be cloned
- Git credentials configured

#### Execution Steps

**### Step 1: Verify V2Ray Status**
- **Action**: Check if V2Ray is running
- **Command**: `systemctl status v2ray --no-pager | head -5`
- **Expected**: `Active: active (running)`
**[Run and report]**

**### Step 2: Test GitHub Connectivity**
- **Action**: Test connection to GitHub
- **Command**: `curl -x http://127.0.0.1:10809 -I https://github.com`
- **Expected**: HTTP 200/301 response
**[Run and report]**

**### Step 3: Detect Changed Skills**
- **Action**: Find modified skills
- **Command**:
  ```bash
  cd ~/openclaw-skills/skills
  git status --short | grep "^ M" | cut -c4-
  ```
- **Expected**: List of modified skills
**[Run and report]**

**### Step 4: Stage and Commit Skills**
- **Action**: Stage and commit skill changes
- **Command**:
  ```bash
  git add skills/
  git commit -m "feat: Update skills - $(date +%Y-%m-%d)"
  ```
- **Expected**: Commit created with hash
**[Run and report commit hash]**

**### Step 5: Push to GitHub**
- **Action**: Push to remote repository
- **Command**:
  ```bash
  export HTTPS_PROXY=http://127.0.0.1:10809
  git push origin main
  ```
- **Expected**: Push successful
**[Run and report]**

**### Step 6: Generate Report**
- **Action**: Create sync report
- **Command**:
  ```bash
  echo "Skills Sync Report - $(date)" > /tmp/skills_sync.log
  git log -1 --oneline >> /tmp/skills_sync.log
  git diff --stat HEAD~1 HEAD >> /tmp/skills_sync.log
  cat /tmp/skills_sync.log
  ```
- **Expected**: Report displayed with change stats
**[Run and display]**

---

## Error Handling

### Step Failure Protocol

**When a step fails:**

1. **Immediately report error:**
   ```
   ❌ Step X 失败：[具体错误信息]
   错误详情：[command output]
   ```

2. **Attempt recovery (if applicable):**
   ```
   🔧 正在尝试恢复...
   恢复方案：[description]
   ```

3. **If recovery succeeds:**
   ```
   ✅ 恢复成功，继续执行
   ```

4. **If recovery fails or not applicable:**
   ```
   ❌ 无法恢复，停止同步
   已完成步骤：X-1
   失败步骤：X
   ```

### Error Recovery Strategies

| Error Type | Recovery Strategy |
|------------|------------------|
| V2Ray not running | Start V2Ray: `sudo systemctl start v2ray` |
| GitHub unreachable | Check proxy, retry with `--force` |
| Merge conflict | Stop and report (manual resolution required) |
| Authentication failed | Update credentials and retry |
| Disk space full | Clean up and retry |
| Network timeout | Retry once with increased timeout |

### Common Error Messages

**V2Ray Not Running:**
```
❌ Step 1 失败：V2Ray 未运行
错误：Active: inactive (dead)
🔧 恢复方案：启动 V2Ray 服务
sudo systemctl start v2ray
```

**GitHub Unreachable:**
```
❌ Step 2 失败：无法连接到 GitHub
错误：Connection timeout
🔧 恢复方案：检查代理配置
curl -x http://127.0.0.1:10809 -I https://github.com
```

**Merge Conflict:**
```
❌ Step 6 失败：Git 合并冲突
错误：CONFLICT (content): Merge conflict in ...
🔧 恢复方案：需要手动解决冲突
git status
# 手动解决冲突后运行：
git add .
git commit
git push
```

**Authentication Failed:**
```
❌ Step 6 失败：GitHub 认证失败
错误：Authentication failed for ...
🔧 恢复方案：更新 Git 凭据
git config --local credential.helper store
# 重新运行 sync
```

---

## User Confirmation Requirements

### Destructive Operations Require Confirmation

**These operations MUST have user confirmation:**

| Operation | Requires Confirmation |
|-----------|---------------------|
| Force push | ✅ Yes |
| Reset to previous commit | ✅ Yes |
| Delete remote branch | ✅ Yes |
| Sync all repos | ⚠️ Recommended |
| Memory sync | ❌ No |
| Skills sync | ❌ No |

### Confirmation Message Format

```
⚠️ 即将执行危险操作：强制推送到 GitHub
📦 仓库：[repo_name]
🔗 远程：[remote_url]
📝 本地提交：[local_commit]
📝 远程提交：[remote_commit]

确认继续？(yes/no)
```

**Only proceed if user responds "yes" or "确认". Any other response → STOP.**

---

## Quick Reference

### Sync Memory
```bash
cd ~/.openclaw/workspace/skills/github-sync/scripts
./sync_memory.sh
```

### Sync Skills
```bash
cd ~/.openclaw/workspace/skills/github-sync/scripts
./sync_skills.sh
```

### Sync All
```bash
cd ~/.openclaw/workspace/skills/github-sync/scripts
./sync_all.sh
```

### Check Status
```bash
cd ~/.openclaw/workspace/skills/github-sync/scripts
./sync_status.sh
```

---

## Configuration

### Repository Config

Edit `config.json`:
```json
{
  "repositories": {
    "memory": {
      "url": "https://github.com/USERNAME/training-memories.git",
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
  }
}
```

---

## Best Practices

1. **Check V2Ray before sync**
2. **Review changes before commit**
3. **Monitor sync logs**
4. **After updating ANY skill, sync to GitHub**

---

## Logs Location

- Sync log: `~/.openclaw/github_sync.log`
- Error log: `~/.openclaw/github_sync_errors.log`
- Config: `~/.openclaw/workspace/skills/github-sync/config.json`

---

## Summary

**Golden Rule: Sync step-by-step with verification.**

- Verify → Stage → Commit → Push → Report
- Stop on any error
- Report progress at each step
- Test connectivity before git operations

Data integrity is priority #1.
