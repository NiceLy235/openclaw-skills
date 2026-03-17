---
name: feishu-realtime
description: |
  Feishu real-time progress feedback for all tasks. MANDATORY for any multi-step Feishu operations.
  Use when: executing ANY Feishu task with multiple steps (doc operations, wiki navigation, drive management).
metadata:
  {
    "openclaw": {
      "emoji": "📱"
    }
  }
---

# Feishu Real-Time Progress Feedback

⚠️ **CRITICAL: Execute steps in strict order as listed below. Do NOT skip any step.**

---

## MANDATORY Execution Rules

1. **Execute steps sequentially** - Complete Step 1 before starting Step 2
2. **Report progress after EACH step** - Send progress message before proceeding to next step
3. **Do NOT skip verification steps** - Always verify API response success before proceeding
4. **Stop on error** - If any Feishu API call fails, report the error and STOP. Do NOT proceed with remaining steps
5. **Require user confirmation for write operations** - For destructive operations (delete, overwrite), ask user to confirm
6. **Real-time feedback** - NEVER wait until completion to report results

---

## Progress Reporting Rules

1. **Start each step** with: `🚀 开始执行步骤 X/Y：[步骤描述]`
2. **After each step**, report: `✅ 步骤 X/Y 完成：[摘要]`
3. **If a step fails**, report: `❌ 步骤 X/Y 失败：[错误描述]` and STOP
4. **Before next step**, briefly indicate: `→ 正在执行步骤 X+1/Y...`

## Error Handling

### Step Failure Protocol

**When a Feishu API call fails:**

1. **Immediately report error:**
   ```
   ❌ 步骤 X 失败：[具体错误信息]
   错误代码：[code]
   错误详情：[details]
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
   ❌ 无法恢复，停止任务
   已完成步骤：X-1
   失败步骤：X
   ```

### Error Recovery Strategies

| Error Type | Recovery Strategy |
|------------|------------------|
| Network timeout | Retry once with 2x timeout |
| Rate limit (429) | Wait 60s, retry |
| Permission denied | Stop and report (no recovery) |
| Resource not found (404) | Stop and report (no recovery) |
| Invalid input | Correct input and retry |

---

## Verification Steps

### After Each API Call

**Verify before proceeding:**

1. **Check response status:**
   ```json
   {
     "action": "verify",
     "check": "response.code == 0",
     "expected": "Success"
   }
   ```

2. **Verify response data (if applicable):**
   ```json
   {
     "action": "verify",
     "check": "response.data != null",
     "expected": "Data returned"
   }
   ```

3. **Only proceed if verification passes:**
   ```
   ✅ 验证通过：API 调用成功
   → 正在执行下一步...
   ```

### Verification Examples

**Document Read Verification:**
```json
// After feishu_doc({ "action": "read", "doc_token": "xxx" })
if (response.code == 0 && response.data.blocks.length > 0) {
  // ✓ Verification passed
  message = "✅ 步骤 1 完成：文档读取成功 (blocks: " + response.data.blocks.length + ")";
} else {
  // ✗ Verification failed
  message = "❌ 步骤 1 失败：文档读取失败";
  STOP;
}
```

**Wiki Create Verification:**
```json
// After feishu_wiki({ "action": "create", ... })
if (response.code == 0 && response.data.node_token) {
  // ✓ Verification passed
  message = "✅ 步骤 1 完成：Wiki 节点创建成功";
} else {
  // ✗ Verification failed
  message = "❌ 步骤 1 失败：Wiki 节点创建失败";
  STOP;
}
```

---

## User Confirmation Requirements

### Destructive Operations Require Confirmation

**These operations MUST have user confirmation:**

| Operation Type | Requires Confirmation |
|---------------|---------------------|
| Delete document/page | ✅ Yes |
| Delete wiki node | ✅ Yes |
| Delete files/folders | ✅ Yes |
| Overwrite existing content | ✅ Yes |
| Move to trash | ✅ Yes |
| Batch delete | ✅ Yes |
| Create/read/edit | ❌ No |

### Confirmation Message Format

```json
{
  "action": "send",
  "channel": "feishu",
  "message": "⚠️ 即将执行危险操作：删除文档\n📄 文档：[文档名称]\n🔗 链接：[文档链接]\n\n确认继续？(yes/no)"
}
```

**Only proceed if user responds "yes" or "确认". Any other response → STOP.**

---

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
// 2.1 Execute API call
feishu_doc({ "action": "read", "doc_token": "xxx" })

// 2.2 Verify response
if (response.code == 0 && response.data != null) {
  // 2.3 Report progress
  {
    "action": "send",
    "channel": "feishu",
    "message": "✅ 步骤 1/3 完成：读取文档内容\n📄 Blocks: " + response.data.blocks.length
  }
} else {
  // 2.4 Report error and STOP
  {
    "action": "send",
    "channel": "feishu",
    "message": "❌ 步骤 1 失败：读取文档失败\n错误代码：" + response.code
  }
  STOP;
}
```

### Step 3: Execute Subsequent Operations

```json
// 3.1 Execute API call
feishu_doc({ "action": "list_blocks", "doc_token": "xxx" })

// 3.2 Verify response
if (response.code == 0) {
  // 3.3 Report progress
  {
    "action": "send",
    "channel": "feishu",
    "message": "✅ 步骤 2/3 完成：获取文档结构\n📊 节点数：" + response.data.items.length
  }
} else {
  // 3.4 Report error and STOP
  {
    "action": "send",
    "channel": "feishu",
    "message": "❌ 步骤 2 失败：获取结构失败"
  }
  STOP;
}
```

### Step 4: Final Completion

```json
// 4.1 Execute final operation
feishu_doc({ "action": "write", "doc_token": "xxx", "content": "..." })

// 4.2 Verify response
if (response.code == 0) {
  // 4.3 Report completion
  {
    "action": "send",
    "channel": "feishu",
    "message": "✅ 全部完成！已更新文档：[文档名称]\n🔗 链接：[doc_url]"
  }
} else {
  // 4.4 Report error and STOP
  {
    "action": "send",
    "channel": "feishu",
    "message": "❌ 步骤 3 失败：写入文档失败"
  }
  STOP;
}
```

## Example: Create Wiki Page with Content

### ❌ WRONG (No Progress Feedback, No Verification)

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
// ❌ NO verification if any step failed
// ❌ NO progress feedback
// ❌ User has no idea which step failed
```

### ✅ RIGHT (Real-Time Progress + Verification)

```json
// 1. Immediate start
{
  "action": "send",
  "channel": "feishu",
  "message": "🚀 开始创建 Wiki 页面..."
}

// 2. Create wiki node
feishu_wiki({ "action": "create", "space_id": "xxx", "title": "New Page" })

// 2.1 Verify response
if (response.code == 0 && response.data.node_token) {
  // 2.2 Report progress
  {
    "action": "send",
    "channel": "feishu",
    "message": "✅ 步骤 1/3 完成：已创建 Wiki 节点\n📝 Token: " + response.data.node_token
  }
} else {
  // 2.3 Report error and STOP
  {
    "action": "send",
    "channel": "feishu",
    "message": "❌ 步骤 1 失败：Wiki 节点创建失败\n错误：" + response.msg
  }
  STOP;
}

// 3. Write content
feishu_doc({ "action": "write", "doc_token": "yyy", "content": "..." })

// 3.1 Verify response
if (response.code == 0) {
  // 3.2 Report progress
  {
    "action": "send",
    "channel": "feishu",
    "message": "✅ 步骤 2/3 完成：已写入内容\n📊 Blocks: " + response.data.blocks.length
  }
} else {
  // 3.3 Report error and STOP
  {
    "action": "send",
    "channel": "feishu",
    "message": "❌ 步骤 2 失败：写入内容失败"
  }
  STOP;
}

// 4. Upload image
feishu_doc({ "action": "upload_image", "doc_token": "yyy", "url": "..." })

// 4.1 Verify response
if (response.code == 0) {
  // 4.2 Report progress
  {
    "action": "send",
    "channel": "feishu",
    "message": "✅ 步骤 3/3 完成：已上传图片\n🖼️ 文件：[file_name]"
  }
} else {
  // 4.3 Report error and STOP
  {
    "action": "send",
    "channel": "feishu",
    "message": "❌ 步骤 3 失败：图片上传失败"
  }
  STOP;
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

## Step-by-Step Execution Template

Use this template for ANY multi-step Feishu operation:

### Step 1: Pre-flight Check
- **Action**: Verify Feishu API access and permissions
- **Check**: Test API connection
- **Expected**: API responds successfully
**[Run check and report]**

### Step 2: Start Notification
- **Action**: Send start message to user
- **Message**: `🚀 开始执行任务：[任务名称]`
- **Expected**: Message sent
**[Send start message]**

### Step 3: Execute Operation 1
- **Action**: Execute Feishu API call
- **Verify**: Check response.code == 0
- **Expected**: Success response
**[Execute → Verify → Report]**

### Step 4: Execute Operation 2
- **Action**: Execute next Feishu API call
- **Verify**: Check response.code == 0
- **Expected**: Success response
**[Execute → Verify → Report]**

### Step 5: ... (Repeat for each operation)
- **Action**: Execute each operation sequentially
- **Verify**: Check response after each
- **Expected**: All operations succeed
**[Execute → Verify → Report for each]**

### Step 6: Final Completion
- **Action**: Send completion message
- **Message**: `✅ 全部完成！[结果摘要]`
- **Expected**: Message sent with summary
**[Send completion message]**

---

## Summary

**Golden Rule: Every step = One message.**

- Start → Progress → Progress → ... → Complete
- Never let user wait in silence
- Better to over-communicate than under-communicate
- **ALWAYS verify before proceeding**
- **STOP on any error**

User experience is priority #1.
