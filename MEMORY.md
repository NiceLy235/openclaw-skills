# MEMORY.md - Long-Term Memory

This file contains important decisions, preferences, and lessons learned that should persist across sessions.

---

## 📱 Feishu Operations - Real-Time Feedback (2026-03-13)

### Critical Decision

**All Feishu tasks MUST show real-time progress feedback.**

### Context

User requested (2026-03-13):
> "我希望让后面所有飞书机器人执行任务的时候，必须把每个步骤都及时展示出来，不能在执行完成后，才返回消息。"

### Implementation

1. **Created Skill**: `feishu-realtime` at `skills/feishu-realtime/SKILL.md`
   - Pushed to GitHub: `NiceLy235/openclaw-skills`
   - Contains detailed real-time feedback workflow

2. **Updated AGENTS.md**: Added mandatory Feishu real-time feedback section
   - Applies to ALL Feishu operations
   - Enforced regardless of which skill is active
   - Persists across all future sessions

3. **Standard Workflow**:
   ```
   🚀 开始执行任务：[任务名称]
   ✅ 步骤 1/N 完成：[步骤描述]
   ✅ 步骤 2/N 完成：[步骤描述]
   ...
   🎉 全部完成！[结果摘要]
   ```

### Rules

- **NEVER** execute >3 Feishu API calls without progress message
- **ALWAYS** send start message before first API call
- **ALWAYS** send completion message after last API call
- **ALWAYS** report errors immediately

### Why Important

- User experience: No silent waits
- Transparency: User knows exactly what's happening
- Better UX for long-running operations

### Applies To

- Document operations (read, write, append, create)
- Wiki navigation (list spaces, create nodes, get nodes)
- Drive management (list folders, create folders, move files)
- Bitable operations (get meta, list fields, create records)
- ALL multi-step Feishu tasks

### Verification

To verify this rule is working:
1. Request any Feishu task with multiple steps
2. Observe real-time progress messages after each step
3. No long silent waits

---

## 🎯 Future Updates

When making important decisions about:
- Workflow changes
- User preferences
- System configuration
- Tool usage patterns

Update this file to ensure continuity across sessions.

---

**Last Updated**: 2026-03-13
**Next Review**: When significant changes occur
