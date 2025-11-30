# CSV Dataset Export Guide

## Overview

The trajectory prediction dataset has been successfully exported to CSV format. The dataset contains drone trajectory sequences with physics-based motion data suitable for machine learning training.

## Generated Files

Location: `/workspace/data/csv/`

### Main Data Files

1. **train_data.csv** (403 MB)
   - 292,523 training samples
   - Used for model training

2. **val_data.csv** (87 MB)
   - 62,683 validation samples
   - Used for hyperparameter tuning and model evaluation during training

3. **test_data.csv** (87 MB)
   - 62,685 test samples
   - Used for final model evaluation

### Supporting Files

4. **normalization.csv**
   - Statistical parameters for data normalization
   - Contains mean and standard deviation for positions and velocities
   - Essential for preprocessing data before model training

5. **dataset_metadata.csv**
   - Dataset configuration and statistics
   - Sequence length, feature counts, sample counts

## Dataset Structure

### Data Format

Each row in the CSV files represents one training sample with:
- **Input sequence**: 10 timesteps × 13 features = 130 columns
- **Target output**: 6 features (next position + velocity)
- **Total columns**: 136

### Column Naming Convention

Columns follow this pattern:
- `t{N}_{feature_name}` - Feature at timestep N
- `target_{feature_name}` - Prediction target

### Features Per Timestep (13 total)

For each of the 10 timesteps (t0 through t9):

1. **Position** (3 features)
   - `t{N}_pos_x` - X position (meters)
   - `t{N}_pos_y` - Y position (meters)
   - `t{N}_pos_z` - Z position (meters)

2. **Velocity** (3 features)
   - `t{N}_vel_x` - X velocity (m/s)
   - `t{N}_vel_y` - Y velocity (m/s)
   - `t{N}_vel_z` - Z velocity (m/s)

3. **Acceleration** (3 features)
   - `t{N}_acc_x` - X acceleration (m/s²)
   - `t{N}_acc_y` - Y acceleration (m/s²)
   - `t{N}_acc_z` - Z acceleration (m/s²)

4. **Target Waypoint** (3 features)
   - `t{N}_target_wp_x` - Target waypoint X position
   - `t{N}_target_wp_y` - Target waypoint Y position
   - `t{N}_target_wp_z` - Target waypoint Z position

5. **Distance** (1 feature)
   - `t{N}_dist_to_wp` - Euclidean distance to target waypoint (meters)

### Target Features (6 total)

The prediction target for the next timestep:

1. **Next Position** (3 features)
   - `target_pos_x` - Next X position
   - `target_pos_y` - Next Y position
   - `target_pos_z` - Next Z position

2. **Next Velocity** (3 features)
   - `target_vel_x` - Next X velocity
   - `target_vel_y` - Next Y velocity
   - `target_vel_z` - Next Z velocity

## Usage Examples

### Python - Loading with Pandas

```python
import pandas as pd

# Load training data
train_df = pd.read_csv('/workspace/data/csv/train_data.csv')

# Load normalization statistics
norm_df = pd.read_csv('/workspace/data/csv/normalization.csv')

# Separate input features and targets
input_cols = [col for col in train_df.columns if col.startswith('t')]
target_cols = [col for col in train_df.columns if col.startswith('target')]

X = train_df[input_cols].values  # Shape: (292523, 130)
y = train_df[target_cols].values  # Shape: (292523, 6)

print(f"Input shape: {X.shape}")
print(f"Target shape: {y.shape}")
```

### Python - Loading with NumPy

```python
import numpy as np

# Load data directly
data = np.loadtxt('/workspace/data/csv/train_data.csv', 
                  delimiter=',', skiprows=1)

# Split into inputs and targets
X = data[:, :130]  # First 130 columns (input sequence)
y = data[:, 130:]  # Last 6 columns (targets)
```

### R - Loading Data

```r
# Load training data
train_data <- read.csv('/workspace/data/csv/train_data.csv')

# Select input and target columns
input_cols <- grep("^t", colnames(train_data), value = TRUE)
target_cols <- grep("^target", colnames(train_data), value = TRUE)

X <- train_data[, input_cols]
y <- train_data[, target_cols]
```

## Data Characteristics

### Trajectory Generation

The dataset was generated using physics-based simulation with:
- 1,000 diverse drone trajectories
- Random initial conditions and waypoints
- Realistic drone dynamics (acceleration limits, drag, etc.)
- 30% of data augmented with Gaussian noise

### Sequence Structure

- **Time step**: 0.1 seconds (100ms)
- **Sequence length**: 10 timesteps = 1 second of history
- **Prediction horizon**: 1 timestep (0.1 seconds ahead)

### Spatial Range

- **Horizontal area**: ±50 meters
- **Altitude range**: 2-20 meters
- **Maximum speed**: 15 m/s horizontal, 5 m/s vertical
- **Maximum acceleration**: 5 m/s²

## Normalization

The `normalization.csv` file contains statistics calculated from the training set:

```
statistic,value
pos_mean_x,-0.339
pos_mean_y,-0.300
pos_mean_z,10.489
pos_std_x,23.579
pos_std_y,23.523
pos_std_z,4.821
vel_mean_x,0.001
vel_mean_y,-0.001
vel_mean_z,-0.037
vel_std_x,6.882
vel_std_y,6.890
vel_std_z,2.293
```

### Normalization Formula

```python
# For positions
normalized_pos = (pos - pos_mean) / pos_std

# For velocities
normalized_vel = (vel - vel_mean) / vel_std
```

## Dataset Statistics

- **Total trajectories**: 1,000
- **Total samples**: 417,891
- **Training samples**: 292,523 (70%)
- **Validation samples**: 62,683 (15%)
- **Test samples**: 62,685 (15%)

## File Sizes

- `train_data.csv`: 403 MB
- `val_data.csv`: 87 MB
- `test_data.csv`: 87 MB
- Total: ~577 MB

## Regenerating CSV Files

To regenerate the CSV files with different parameters:

```bash
# Generate new dataset with custom number of trajectories
cd /workspace/python
python3 data_generator.py  # Modify parameters in the script

# Export to CSV
python3 export_dataset_to_csv.py

# Or with custom options
python3 export_dataset_to_csv.py --data_dir ../data --output_dir ../data/csv
```

## Notes

- The CSV format is more portable but larger than the original pickle format
- All data is in float32 precision
- Headers are included in all CSV files
- Files use comma (`,`) as delimiter
- No missing values or NaN entries
- Data is already shuffled in the pickle files before export

## Related Files

- **Original pickle data**: `/workspace/data/*.pkl`
- **Data generation script**: `/workspace/python/data_generator.py`
- **Export script**: `/workspace/python/export_dataset_to_csv.py`
- **Training script**: `/workspace/python/train_model.py`
