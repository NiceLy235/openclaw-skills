---
name: feishu-realtime
description: |
  Feishu real-time progress feedback for all tasks. MANDATORY for any multi-step Feishu operations.
  Use when: executing ANY Feishu task with multiple steps (doc operations, wiki navigation, drive management).
---

# Feishu Real-Time Progress Feedback

**CRITICAL RULE: Every Feishu task MUST show real-time progress. NEVER wait until completion to report results.**

## Why Real-Time Feedback?

- ✅ User knows task is in progress (not stuck)
- ✅ User can see which step is executing
- ✅ Better experience for long-running operations
- ✅ Follows AGENTS.md "Long-Running Commands" principle

## Progress Report Rules

### Quick Tasks (<10s)
- Execute and report immediately
- Still show a brief "执行中..." message if there's any delay

### Medium Tasks (10-60s)
- Send **immediate** start message
- Send **2-3** progress updates during execution
- Send **completion** message with results

### Long Tasks (>1min)
- Send **immediate** start message
- Send **continuous** updates every 10-30s
- Send **completion** message with summary

### Unknown Duration
- Send **immediate** start message
- Send **adaptive** updates (start with 10s intervals)
- Send **completion** message when done

## Standard Workflow

### Step 1: Immediate Start Notification

```json
{
  "action": "send",
  "channel": "feishu",
  "message": "🚀 开始执行任务：[任务名称]"
}
```

### Step 2: Execute First Operation

```json
// Execute first API call
feishu_doc({ "action": "read", "doc_token": "xxx" })

// Report progress
{
  "action": "send",
  "channel": "feishu",
  "message": "✅ 步骤 1/3 完成：读取文档内容"
}
```

### Step 3: Execute Subsequent Operations

```json
// Execute second API call
feishu_doc({ "action": "list_blocks", "doc_token": "xxx" })

// Report progress
{
  "action": "send",
  "channel": "feishu",
  "message": "✅ 步骤 2/3 完成：获取文档结构"
}
```

### Step 4: Final Completion

```json
// Execute final operation
feishu_doc({ "action": "write", "doc_token": "xxx", "content": "..." })

// Report completion
{
  "action": "send",
  "channel": "feishu",
  "message": "✅ 全部完成！已更新文档：[文档名称]"
}
```

## Example: Create Wiki Page with Content

### ❌ WRONG (No Progress Feedback)

```json
// User waits in silence...
feishu_wiki({ "action": "create", "space_id": "xxx", "title": "New Page" })
feishu_doc({ "action": "write", "doc_token": "yyy", "content": "..." })
feishu_doc({ "action": "upload_image", "doc_token": "yyy", "url": "..." })

// Only now user sees result (too late!)
{
  "action": "send",
  "channel": "feishu",
  "message": "✅ 创建完成"
}
```

### ✅ RIGHT (Real-Time Progress)

```json
// 1. Immediate start
{
  "action": "send",
  "channel": "feishu",
  "message": "🚀 开始创建 Wiki 页面..."
}

// 2. Create wiki node
feishu_wiki({ "action": "create", "space_id": "xxx", "title": "New Page" })
{
  "action": "send",
  "channel": "feishu",
  "message": "✅ 步骤 1/3：已创建 Wiki 节点"
}

// 3. Write content
feishu_doc({ "action": "write", "doc_token": "yyy", "content": "..." })
{
  "action": "send",
  "channel": "feishu",
  "message": "✅ 步骤 2/3：已写入内容"
}

// 4. Upload image
feishu_doc({ "action": "upload_image", "doc_token": "yyy", "url": "..." })
{
  "action": "send",
  "channel": "feishu",
  "message": "✅ 步骤 3/3：已上传图片"
}

// 5. Completion
{
  "action": "send",
  "channel": "feishu",
  "message": "🎉 全部完成！Wiki 页面已创建：[链接]"
}
```

## Progress Message Format

### Start Message
```
🚀 开始执行任务：[任务名称]
```

### Progress Message
```
✅ 步骤 X/Y 完成：[步骤描述]
```

Or with details:
```
✅ 步骤 X/Y 完成：[步骤描述]
📄 [具体信息，如文件名、行数等]
```

### Completion Message
```
✅ 全部完成！[结果摘要]
```

Or with details:
```
🎉 任务完成！
📊 处理结果：
- 文档数：3
- 表格数：2
- 图片数：5
⏱️ 耗时：45秒
```

### Error Message
```
❌ 步骤 X 失败：[错误描述]
🔧 正在尝试：[恢复方案]
```

## What to Report

### ✅ MUST Report
- Task start (immediate)
- Each major step completion
- Errors encountered
- Final completion with summary

### 📊 GOOD to Report
- File/document names being processed
- Progress percentage (if known)
- Time elapsed (for long tasks)
- Items processed count

### ❌ DON'T Report
- Internal API call details
- Debug information
- Technical stack traces (unless error)

## Special Cases

### Parallel Operations
When executing multiple independent operations in parallel:

```json
{
  "action": "send",
  "channel": "feishu",
  "message": "🔄 正在并行处理 5 个文档..."
}

// Execute parallel operations
// ...

{
  "action": "send",
  "channel": "feishu",
  "message": "✅ 已完成 5/5 个文档处理"
}
```

### Long-Running Tasks (Training, Bulk Operations)
For tasks taking >5 minutes:

```json
{
  "action": "send",
  "channel": "feishu",
  "message": "🚀 开始批量处理 100 个文档（预计耗时 10 分钟）"
}

// Every 30 seconds
{
  "action": "send",
  "channel": "feishu",
  "message": "📊 进度：45/100 (45%) | 已处理 45 个文档"
}

// Completion
{
  "action": "send",
  "channel": "feishu",
  "message": "🎉 批量处理完成！\n✅ 成功：98\n❌ 失败：2\n⏱️ 总耗时：12分钟"
}
```

## Enforcement Rules

1. **NEVER execute >3 Feishu API calls without at least one progress message**
2. **ALWAYS send start message before first API call**
3. **ALWAYS send completion message after last API call**
4. **ALWAYS report errors immediately with recovery attempt**

## Integration with AGENTS.md

This skill enforces the "Long-Running Commands - Real-Time Feedback" principle from AGENTS.md specifically for Feishu operations.

Key principle from AGENTS.md:
> **ALWAYS provide real-time feedback for long-running commands (>10 seconds).**
> User experience first. Active communication, not silent waits.

## Examples by Task Type

### Document Operations
- Create → Read → Write → Upload Image
- Each step = one progress message

### Wiki Navigation
- List Spaces → List Nodes → Get Node → Read Doc
- Report at each navigation step

### Drive Management
- List Folders → Create Folder → Move Files
- Report each file operation

### Bitable Operations
- Get Meta → List Fields → Create Record → Update Record
- Report each database operation

## Configuration

No special configuration needed. This skill activates automatically for all Feishu tasks.

```yaml
# Optional: Adjust progress report interval for long tasks
feishu:
  progressInterval: 30s  # Default: 30 seconds
```

## Summary

**Golden Rule: Every step = One message.**

- Start → Progress → Progress → ... → Complete
- Never let user wait in silence
- Better to over-communicate than under-communicate

User experience is priority #1.
