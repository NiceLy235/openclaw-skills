# LeRobot Installation Guide

## Overview

LeRobot is a Python library for robot learning and reinforcement learning. This guide provides detailed information about LeRobot installation and configuration.

## System Requirements

### Minimum Requirements
- **Operating System**: Ubuntu 20.04+, Debian 11+, or macOS
- **Python**: 3.8 or higher
- **Disk Space**: Minimum 2GB (5GB recommended with GPU support)
- **RAM**: 4GB minimum, 8GB recommended

### Recommended Requirements (for GPU acceleration)
- **NVIDIA GPU**: CUDA-capable GPU (GTX 1060 or better)
- **CUDA**: Version 11.7 or higher
- **cuDNN**: Version 8.0 or higher
- **GPU Memory**: 4GB minimum, 8GB recommended

## Installation Methods

### Method 1: Automated Installation (Recommended)

Use the provided script:

```bash
bash scripts/install_lerobot.sh
```

### Method 2: Manual Installation

#### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git \
    python3-dev libopenblas-dev liblapack-dev gfortran libhdf5-dev
```

**macOS:**
```bash
brew install python3 git
```

#### Step 2: Create Virtual Environment

```bash
mkdir -p ~/opt/lerobot
cd ~/opt/lerobot
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install PyTorch

**With CUDA support (Linux):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**CPU only:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### Step 4: Install LeRobot

```bash
pip install --upgrade pip setuptools wheel
pip install lerobot
```

## GPU Configuration

### Check CUDA Installation

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA compiler
nvcc --version

# Check CUDA in PyTorch
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python3 -c "import torch; print(f'CUDA version: {torch.version.cuda}')"
python3 -c "import torch; print(f'GPU count: {torch.cuda.device_count()}')"
```

### Install CUDA Toolkit (if needed)

**Ubuntu:**
```bash
# Add NVIDIA package repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600

sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"

sudo apt-get update
sudo apt-get -y install cuda
```

## Usage

### Activate Environment

```bash
source ~/opt/lerobot/activate.sh
```

Or manually:
```bash
source ~/opt/lerobot/venv/bin/activate
```

### Verify Installation

```python
import lerobot
print(f"LeRobot version: {lerobot.__version__}")

import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

### Basic Example

```python
from lerobot.common.policies.act.modeling_act import ACTPolicy

# Load a pre-trained policy
policy = ACTPolicy.from_pretrained("lerobot/act_aloha_sim_transfer_cube")

# Use the policy for inference
# (See LeRobot documentation for complete examples)
```

## Configuration

### Environment Variables

```bash
# Set cache directory for Hugging Face models
export HF_HOME="~/.cache/huggingface"

# Set PyTorch CUDA memory fraction
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Force CPU-only mode (if needed)
export CUDA_VISIBLE_DEVICES=""
```

### Jupyter Notebook Integration

```bash
# Install Jupyter in the virtual environment
pip install jupyter

# Create a kernel
python -m ipykernel install --user --name=lerobot --display-name="LeRobot"

# Start Jupyter
jupyter notebook
```

## Common Dependencies

LeRobot automatically installs these dependencies:
- `torch` - PyTorch deep learning framework
- `transformers` - Hugging Face Transformers
- `datasets` - Hugging Face Datasets
- `gymnasium` - RL environments
- `opencv-python` - Computer vision
- `numpy`, `scipy` - Numerical computing
- `tensorboard` - Training visualization

## Performance Optimization

### GPU Memory Management

```python
import torch

# Clear cache
torch.cuda.empty_cache()

# Set memory fraction
torch.cuda.set_per_process_memory_fraction(0.8, 0)

# Monitor memory
print(torch.cuda.memory_summary())
```

### Mixed Precision Training

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

with autocast():
    # Your training code
    pass
```

## Updating

```bash
source ~/opt/lerobot/activate.sh
pip install --upgrade lerobot
```

## Uninstallation

```bash
# Simply remove the installation directory
rm -rf ~/opt/lerobot
```

## Additional Resources

- [Official Documentation](https://github.com/huggingface/lerobot)
- [Hugging Face LeRobot Models](https://huggingface.co/lerobot)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
