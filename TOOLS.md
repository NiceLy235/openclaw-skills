# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 🌐 V2Ray Proxy Configuration

### Local Machine (nice)

**V2Ray Service:**
- Config: `/usr/local/etc/v2ray/config.json`
- SOCKS5: `127.0.0.1:10808`
- HTTP: `127.0.0.1:10809`
- Service: `systemctl status v2ray`

**Proxy Environment Variables (MUST SET BEFORE TRAINING):**
```bash
export HTTP_PROXY=http://127.0.0.1:10809
export HTTPS_PROXY=http://127.0.0.1:10809
export ALL_PROXY=socks5://127.0.0.1:10808
```

**Permanent Configuration:**
```bash
# Add to ~/.bashrc
echo 'export HTTP_PROXY=http://127.0.0.1:10809' >> ~/.bashrc
echo 'export HTTPS_PROXY=http://127.0.0.1:10809' >> ~/.bashrc
source ~/.bashrc
```

**Connectivity Test:**
```bash
# Test HuggingFace (CRITICAL for model downloads)
curl -I -m 10 https://huggingface.co

# Expected: HTTP/2 200
```

**Proxy Check Script:**
```bash
# Before any training task
bash ~/.openclaw/workspace/skills/lerobot-auto-train/scripts/check_proxy.sh
```

### Remote Servers

**For remote training servers (e.g., connect.westb.seetacloud.com):**

1. **Install v2ray** (use env-setup skill)
2. **Copy config from local:**
   ```bash
   # Local machine
   scp -P PORT /usr/local/etc/v2ray/config.json user@remote:/etc/v2ray/
   ```
3. **Set environment variables on remote:**
   ```bash
   export HTTP_PROXY=http://127.0.0.1:10809
   export HTTPS_PROXY=http://127.0.0.1:10809
   ```
4. **Test connectivity:**
   ```bash
   curl -I https://huggingface.co
   ```

### LeRobot Training Checklist

**Before starting ANY training task:**

1. ✅ Check proxy environment variables: `env | grep -i proxy`
2. ✅ Test HuggingFace: `curl -I https://huggingface.co`
3. ✅ Check v2ray service: `systemctl status v2ray`
4. ✅ Verify GPU available: `nvidia-smi`
5. ✅ Check disk space: `df -h ~`

**If ANY check fails, DO NOT start training. Fix the issue first.**

---

Add whatever helps you do your job. This is your cheat sheet.
