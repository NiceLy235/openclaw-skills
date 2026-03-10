# Lerobot Auto Train - 快速入门指南

## 📦 Skill 已创建！

位置: `skills/lerobot-auto-train/`
打包文件: `lerobot-auto-train.skill`

## 🚀 核心功能

### 1. 环境检查与自动修复
自动检测并修复训练环境问题：
- ✅ 检查是否在 lerobot_ros2 仓库
- ✅ 检查 Python 环境
- ✅ 检查 CUDA 可用性
- ✅ 检查依赖包
- ✅ 检查配置文件

### 2. 后台训练任务
- ✅ 提交后立即返回，不阻塞
- ✅ 在后台执行训练
- ✅ 可以同时运行多个任务
- ✅ 任务队列管理

### 3. 实时进度监控
- ✅ 每 60 秒更新进度（可配置）
- ✅ 显示当前 Epoch/Loss
- ✅ GPU 利用率和显存监控
- ✅ 预估剩余时间

### 4. 任务管理
- ✅ 查询任务状态
- ✅ 停止/恢复任务
- ✅ 查看日志
- ✅ 从检查点恢复

### 5. 推理测试
- ✅ 单样本推理
- ✅ 批量推理
- ✅ 性能基准测试
- ✅ 生成测试报告

## 📖 使用示例

### 示例 1: 环境检查

```bash
cd /path/to/lerobot_ros2

# 检查环境
python skills/lerobot-auto-train/scripts/check_environment.py

# 自动修复
python skills/lerobot-auto-train/scripts/check_environment.py --auto-fix
```

### 示例 2: 提交训练任务

```bash
# 最简提交
python scripts/task_manager.py submit \
  --task-type bc \
  --data-sources data/episodes.h5 \
  --model-name smolvla_base

# 完整参数
python scripts/task_manager.py submit \
  --task-type bc \
  --data-sources data/ep1.h5 data/ep2.h5 \
  --model-name smolvla_base \
  --epochs 100 \
  --batch-size 32 \
  --background \
  --progress-interval 60
```

返回示例:
```
✅ Task submitted: train_20260310_143000_abc123
🚀 Training started in background (PID: 12345)
```

### 示例 3: 监控训练

```bash
# 实时监控（持续更新）
python scripts/progress_monitor.py train_20260310_143000_abc123

# 输出示例:
# 👀 Watching task...
# 🚀 [███████░░░] 70% Epoch 70/100 | Loss: 0.234 | GPU: 85%, 7.2GB/12GB
```

### 示例 4: 管理任务

```bash
# 查看状态
python scripts/task_manager.py status train_20260310_143000_abc123

# 列出所有任务
python scripts/task_manager.py list

# 停止任务
python scripts/task_manager.py stop train_20260310_143000_abc123

# 恢复任务
python scripts/task_manager.py resume train_20260310_143000_abc123

# 查看日志
python scripts/task_manager.py logs train_20260310_143000_abc123
```

### 示例 5: 推理测试

```bash
# 完整测试套件
python scripts/inference_test.py output/model.pt full --output report.md

# 性能基准
python scripts/inference_test.py output/model.pt benchmark --runs 100

# 输出示例:
# ⚡ Mean Latency: 23.4ms
# ⚡ Throughput: 42.7 FPS
```

## 🎯 典型工作流程

```bash
# 1. 进入仓库
cd /path/to/lerobot_ros2

# 2. 检查环境
python scripts/check_environment.py

# 3. 提交训练（后台运行）
python scripts/task_manager.py submit \
  --task-type bc \
  --data-sources data/*.h5 \
  --model-name smolvla_base \
  --background

# 4. 继续其他工作...
# 训练在后台进行，不阻塞你

# 5. 定期检查进度
python scripts/progress_monitor.py <task_id>

# 6. 训练完成后测试
python scripts/inference_test.py output/model.pt full
```

## 📊 输出目录结构

```
output/
├── model.pt              # 最终模型
├── checkpoints/
│   ├── best_model.pt     # 最佳验证模型
│   ├── checkpoint_epoch_10.pt
│   └── ...
└── logs/
    └── training.log

~/.openclaw/tasks/<task_id>/
├── meta.json             # 任务元数据
└── training_<id>.log     # 完整日志
```

## 🔧 配置参数

### 常用参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--epochs` | 100 | 训练轮数 |
| `--batch-size` | 32 | 批次大小（显存不足时减小） |
| `--learning-rate` | 0.001 | 学习率 |
| `--device` | cuda | 设备 (cuda/cpu) |
| `--background` | true | 后台执行 |
| `--progress-interval` | 60 | 进度更新间隔（秒） |

### Batch Size 建议

- RTX 4090/3090 (24GB): 32-64
- RTX 4080/3080 (16GB): 16-32
- RTX 3070/4060 (8GB): 8-16

## 🚨 故障排查

### 环境问题

```bash
# 不在 lerobot_ros2 仓库
cd /path/to/lerobot_ros2

# CUDA 不可用
nvidia-smi  # 检查驱动
# 或使用 CPU
python scripts/task_manager.py submit ... --device cpu
```

### GPU 显存不足

```bash
# 自动减小 batch_size 重试
# 或手动设置
python scripts/task_manager.py submit ... --batch-size 16
```

### 任务失败

```bash
# 1. 查看日志
python scripts/task_manager.py logs <task_id>

# 2. 修复问题

# 3. 恢复任务
python scripts/task_manager.py resume <task_id>
```

## 📚 详细文档

- **任务状态**: `references/task_states.md`
- **错误处理**: `references/error_handling.md`
- **配置格式**: `references/config_schema.md`

## ✨ 特色功能

### 1. 实时反馈
遵循 AGENTS.md 的实时反馈规则：
- 每 5 秒检查进度
- 向用户报告状态
- 不长时间等待无反馈

### 2. 自动恢复
- GPU OOM → 自动减小 batch_size 重试
- 训练中断 → 自动保存检查点
- 进程崩溃 → 可从检查点恢复

### 3. 后台执行
- 训练在后台进行
- openclaw 可以处理其他任务
- 通过 task_id 管理

## 🎉 开始使用

Skill 已就绪！你可以直接使用：

```bash
# 检查环境
python skills/lerobot-auto-train/scripts/check_environment.py

# 提交第一个训练任务
python skills/lerobot-auto-train/scripts/task_manager.py submit \
  --task-type bc \
  --data-sources <你的数据> \
  --model-name smolvla_base \
  --background
```

需要帮助？查看 SKILL.md 或参考文档！
