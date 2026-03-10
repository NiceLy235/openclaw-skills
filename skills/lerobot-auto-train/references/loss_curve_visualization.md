# Loss Curve Visualization Guide

This guide explains how to use automatic validation and loss curve visualization during training.

## Overview

The lerobot-auto-train skill automatically:
- ✅ Validates model on validation set at each checkpoint
- ✅ Records training and validation losses
- ✅ Generates loss curve plots on training completion
- ✅ Saves loss history in JSON format

## Quick Start

### 1. Prepare Dataset with Validation Set

```bash
python scripts/prepare_dataset.py \
  --data-dir /path/to/raw_data \
  --output-dir ./processed_data \
  --train-ratio 0.8
```

This creates:
- `processed_data/train/` - Training set
- `processed_data/val/` - Validation set

### 2. Train with Validation

```bash
python scripts/task_manager.py submit \
  --data-sources ./processed_data/train/ \
  --validation-data ./processed_data/val/ \
  --model-name smolvla_base \
  --epochs 100 \
  --save-freq 10 \
  --background
```

### 3. Automatic Outputs

During training, the system automatically:
1. Validates at every `--save-freq` checkpoint
2. Records training and validation losses
3. Saves loss history to `loss_history.json`

After training completes:
4. Generates loss curve plots
5. Saves as PNG and PDF

## Output Files

```
output/
├── loss_history.json           # Loss data (JSON)
├── loss_curves.png             # Separate train/val curves
├── loss_curves.pdf             # High-quality PDF
└── loss_curves_combined.png    # Combined curves
```

### loss_history.json

```json
{
  "train": [
    {"step": 100, "epoch": 1, "loss": 0.234},
    {"step": 200, "epoch": 2, "loss": 0.198},
    ...
  ],
  "val": [
    {"step": 100, "epoch": 1, "loss": 0.256, "metrics": {...}},
    {"step": 200, "epoch": 2, "loss": 0.212, "metrics": {...}},
    ...
  ]
}
```

## Manual Usage

### Record Training Loss

```bash
python scripts/validate_and_plot.py \
  --output-dir ./output \
  --step 100 \
  --epoch 1 \
  --train-loss 0.234
```

### Validate Model

```bash
python scripts/validate_and_plot.py \
  --model-path ./output/checkpoints/checkpoint_01000.pt \
  --val-data ./processed_data/val/ \
  --output-dir ./output \
  --step 1000 \
  --epoch 10
```

### Plot Only

```bash
python scripts/validate_and_plot.py \
  --output-dir ./output \
  --plot-only
```

### Combined Plot

```bash
python scripts/validate_and_plot.py \
  --output-dir ./output \
  --plot-only \
  --plot-combined
```

## Visualization Examples

### Separate Curves (loss_curves.png)

Two subplots:
- Left: Training loss over steps
- Right: Validation loss with best loss marker

### Combined Curve (loss_curves_combined.png)

Single plot:
- Blue line: Training loss
- Red line: Validation loss
- Green star: Best validation loss

## Best Practices

### 1. Checkpoint Frequency

Set appropriate `--save-freq`:
- **Small datasets**: 5-10 epochs
- **Medium datasets**: 10-20 epochs
- **Large datasets**: 20-50 epochs

```bash
--save-freq 10  # Validate every 10 epochs
```

### 2. Validation Set Size

- **Minimum**: 10-20% of data
- **Recommended**: 20% (default)
- **Small datasets**: Use cross-validation

```bash
--train-ratio 0.8  # 80% train, 20% val
```

### 3. Monitor During Training

Check loss curves periodically:
```bash
# View latest plot
xdg-open output/loss_curves_combined.png

# Or check loss history
cat output/loss_history.json | jq '.val[-5:]'
```

### 4. Identify Overfitting

Signs of overfitting:
- Training loss ↓, Validation loss ↑
- Gap between train/val increases

Solutions:
- Reduce model complexity
- Increase regularization
- Get more data
- Early stopping

## Troubleshooting

### No validation losses recorded

**Cause**: No validation data or validation not triggered

**Solution**:
```bash
# Check validation data exists
ls processed_data/val/

# Ensure --validation-data is specified
--validation-data ./processed_data/val/
```

### Plots not generated

**Cause**: matplotlib not installed or display issues

**Solution**:
```bash
# Install matplotlib
pip install matplotlib

# Use Agg backend (already configured in script)
# Check script uses: matplotlib.use('Agg')
```

### Missing checkpoints

**Cause**: Training didn't reach checkpoint save frequency

**Solution**:
```bash
# Reduce save frequency
--save-freq 5  # Save every 5 epochs

# Or check training completed successfully
cat output/logs/training.log
```

## Advanced Usage

### Custom Plot Styling

Edit `validate_and_plot.py` to customize:
- Colors
- Line styles
- Markers
- Figure size
- DPI

### Export for Papers

Use high-quality PDF:
```bash
# PDF at 300 DPI
python scripts/validate_and_plot.py \
  --output-dir ./output \
  --plot-only

# PDF saved to: output/loss_curves.pdf
```

### Compare Multiple Runs

```bash
# Run 1
python scripts/validate_and_plot.py \
  --output-dir ./output_run1 \
  --plot-only

# Run 2
python scripts/validate_and_plot.py \
  --output-dir ./output_run2 \
  --plot-only

# Compare plots manually
```

## Integration with Training Pipeline

The validation and plotting is fully integrated:

```
Training Loop:
  For each epoch:
    1. Train on training set
    2. Record training loss
    3. If checkpoint save:
       a. Save checkpoint
       b. Validate on val set
       c. Record validation loss
    4. Continue training
  
  After training:
    5. Generate loss curves
    6. Save plots (PNG + PDF)
    7. Save loss history (JSON)
```

## Next Steps

After reviewing loss curves:

1. **Good fit**: Deploy model
2. **Overfitting**: Regularize or get more data
3. **Underfitting**: Increase model complexity or train longer
4. **Unstable**: Reduce learning rate or increase batch size
