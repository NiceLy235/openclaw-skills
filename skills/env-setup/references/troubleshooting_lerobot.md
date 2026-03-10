# LeRobot 环境故障排查指南

## 常见问题和解决方案

### 1. PyTorch 和 torchvision 版本不匹配

**症状**:
```
RuntimeError: operator torchvision::nms does not exist
```

**原因**:
PyTorch 和 torchvision 版本不匹配。例如：
- PyTorch 2.5.1 应该配 torchvision 0.20.1
- PyTorch 2.10.0 应该配 torchvision 0.25.0

**解决方案**:

#### 方案 A: 使用自动修复脚本

```bash
cd ~/.openclaw/workspace/skills/env-setup/scripts
python3 resolve_dependencies.py --fix
```

#### 方案 B: 手动修复

1. 检查当前版本:
   ```bash
   source ~/opt/lerobot/venv/bin/activate
   python3 -c "import torch, torchvision; print(f'torch={torch.__version__}, torchvision={torchvision.__version__}')"
   ```

2. 重新安装匹配的版本:
   ```bash
   # 对于 CUDA 12.1
   pip install --force-reinstall torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
   
   # 或者对于 CUDA 12.8
   pip install --force-reinstall torch==2.10.0 torchvision==0.25.0 --index-url https://download.pytorch.org/whl/cu128
   ```

3. 验证:
   ```bash
   python3 -c "import torch, torchvision; print('OK')"
   ```

---

### 2. 依赖版本冲突

**症状**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
lerobot 0.4.4 requires huggingface-hub<0.36.0,>=0.34.2, but you have huggingface-hub 1.6.0
```

**原因**:
某些包的版本不满足 lerobot 的要求。

**解决方案**:

#### 使用依赖冲突解决脚本

```bash
cd ~/.openclaw/workspace/skills/env-setup/scripts
python3 resolve_dependencies.py --check --fix
```

#### 手动安装指定版本

```bash
source ~/opt/lerobot/venv/bin/activate

# 安装兼容版本
pip install --force-reinstall \
  "huggingface-hub>=0.34.2,<0.36.0" \
  "packaging>=24.2,<26.0" \
  "protobuf>=3.19.0,<7"
```

---

### 3. 缺少依赖包

**症状**:
```
ImportError: Package `num2words` is required to run SmolVLM processor
```

**解决方案**:

```bash
source ~/opt/lerobot/venv/bin/activate
pip install num2words transformers accelerate sentencepiece
```

或者使用完整安装：

```bash
cd ~/.openclaw/workspace/skills/env-setup/scripts
./install_lerobot_enhanced.sh
```

---

### 4. 无法访问 HuggingFace

**症状**:
```
OSError: Can't load processor for 'HuggingFaceTB/SmolVLM2-500M-Video-Instruct'
ERROR: Network is unreachable
```

**原因**:
网络限制，无法直接访问 huggingface.co

**解决方案**:

#### 方案 A: 使用 V2Ray 代理

1. 确保 V2Ray 正在运行:
   ```bash
   sudo systemctl status v2ray
   ```

2. 如果未运行，启动它:
   ```bash
   sudo systemctl start v2ray
   ```

3. 在训练脚本中配置代理:
   ```bash
   export HTTP_PROXY=http://127.0.0.1:10809
   export HTTPS_PROXY=http://127.0.0.1:10809
   export ALL_PROXY=http://127.0.0.1:10809
   ```

4. 或者使用激活脚本（自动配置代理）:
   ```bash
   source ~/opt/lerobot/activate.sh
   ```

#### 方案 B: 使用镜像站（中国用户）

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

---

### 5. CUDA 不可用

**症状**:
```
torch.cuda.is_available() = False
```

**诊断步骤**:

1. 检查 GPU 是否被识别:
   ```bash
   nvidia-smi
   ```

2. 检查驱动是否正确安装:
   ```bash
   lspci -k | grep -i nvidia
   ```
   
   应该看到: `Kernel driver in use: nvidia`

3. 如果显示 `nouveau`，需要禁用:
   ```bash
   # 禁用 nouveau
   echo "blacklist nouveau" | sudo tee /etc/modprobe.d/blacklist-nvidia-nouveau.conf
   echo "options nouveau modeset=0" | sudo tee -a /etc/modprobe.d/blacklist-nvidia-nouveau.conf
   
   # 更新 initramfs
   sudo update-initramfs -u
   
   # 重启
   sudo reboot
   ```

4. 检查 PyTorch CUDA 版本:
   ```bash
   python3 -c "import torch; print(f'PyTorch CUDA: {torch.version.cuda}')"
   ```

**解决方案**:

重新安装带 CUDA 的 PyTorch（参考问题 1 的解决方案）

---

### 6. torchvision 导入错误

**症状**:
```
ImportError: cannot import name 'image' from 'PIL'
```

**原因**:
Pillow 版本不兼容

**解决方案**:

```bash
source ~/opt/lerobot/venv/bin/activate
pip install --upgrade Pillow>=9.0.0
```

---

### 7. 训练时 GPU OOM (Out of Memory)

**症状**:
```
RuntimeError: CUDA out of memory
```

**解决方案**:

1. 减小 batch size:
   ```bash
   lerobot-train ... --batch_size 16  # 从 32 减小到 16
   ```

2. 或者更小:
   ```bash
   lerobot-train ... --batch_size 8
   ```

3. 清空 GPU 缓存:
   ```python
   import torch
   torch.cuda.empty_cache()
   ```

---

### 8. Git 相关错误

**症状**:
```
FileExistsError: Output directory ... already exists and resume is False
```

**解决方案**:

方案 A: 删除旧目录
```bash
rm -rf outputs/train/2026-03-10/15-41-29_smolvla
```

方案 B: 使用新的输出目录
```bash
lerobot-train ... --output_dir outputs/train/my_new_run
```

---

## 诊断工具

### 完整环境检查

```bash
cd ~/.openclaw/workspace/skills/env-setup/scripts
python3 resolve_dependencies.py --report
```

### 生成诊断报告

```bash
# 保存完整诊断信息
python3 resolve_dependencies.py --report > ~/lerobot_diagnostics.txt
```

### 快速验证脚本

创建 `verify_env.sh`:

```bash
#!/bin/bash
source ~/opt/lerobot/activate.sh

echo "=== 环境验证 ==="
python3 << 'EOF'
import sys

print("\n📦 包检查:")
packages = [
    ("torch", "PyTorch"),
    ("torchvision", "torchvision"),
    ("lerobot", "LeRobot"),
    ("transformers", "Transformers"),
    ("num2words", "num2words"),
]

all_ok = True
for module, name in packages:
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"  ✅ {name}: {version}")
    except ImportError as e:
        print(f"  ❌ {name}: 缺失")
        all_ok = False

print("\n🖥️  CUDA 检查:")
try:
    import torch
    if torch.cuda.is_available():
        print(f"  ✅ CUDA: {torch.version.cuda}")
        print(f"  ✅ GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("  ⚠️  CPU 模式")
except:
    print("  ❌ CUDA 检查失败")
    all_ok = False

print("\n" + "="*50)
if all_ok:
    print("✅ 所有检查通过！")
    sys.exit(0)
else:
    print("⚠️  存在问题，需要修复")
    sys.exit(1)
EOF
```

运行:
```bash
chmod +x verify_env.sh
./verify_env.sh
```

---

## 完全重新安装

如果问题太多，建议完全重新安装:

```bash
# 1. 备份数据
cp -r ~/opt/lerobot ~/opt/lerobot.backup

# 2. 删除旧安装
rm -rf ~/opt/lerobot

# 3. 使用增强版脚本重新安装
cd ~/.openclaw/workspace/skills/env-setup/scripts
./install_lerobot_enhanced.sh
```

---

## 获取帮助

如果以上方法都无法解决问题:

1. 收集诊断信息:
   ```bash
   python3 resolve_dependencies.py --report > diagnostics.txt
   nvidia-smi >> diagnostics.txt
   pip list >> diagnostics.txt
   ```

2. 查看日志:
   ```bash
   tail -100 ~/.openclaw/install_lerobot_*.log
   ```

3. 联系支持:
   - GitHub Issues: https://github.com/huggingface/lerobot/issues
   - OpenClaw 社区: https://discord.gg/clawd

---

## 预防措施

### 1. 使用虚拟环境

始终使用虚拟环境，避免全局安装:
```bash
source ~/opt/lerobot/activate.sh
```

### 2. 定期验证

定期运行验证脚本:
```bash
python3 resolve_dependencies.py --check
```

### 3. 备份工作环境

在修改环境前备份:
```bash
cp -r ~/opt/lerobot ~/opt/lerobot.backup_$(date +%Y%m%d)
```

### 4. 记录安装过程

保留安装日志:
```bash
tail -100 ~/.openclaw/install_lerobot_enhanced_*.log
```
