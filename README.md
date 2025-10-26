# Hidden Markov Models for Human Activity Recognition

This project implements Hidden Markov Models (HMM) to recognize human activities from smartphone accelerometer and gyroscope sensor data.

## Project Overview

We collected motion sensor data for four activities (Jumping, Standing, Still, Walking) and trained an HMM to classify these activities from continuous sensor streams. The project demonstrates the application of probabilistic sequential models for real-world human activity recognition.

## Dataset

- **Total Recordings:** 50 sessions across 4 activities
- **Total Data Points:** 57,870 sensor readings
- **Activities Recorded:**
  - Jumping: 11 sessions (12,207 rows)
  - Standing: 13 sessions (15,164 rows)
  - Still: 11 sessions (12,915 rows)
  - Walking: 15 sessions (17,584 rows)
- **Sampling Rate:** 100 Hz
- **Features:** 59 time-domain + frequency-domain features

## Key Features

### Data Processing
- Automatic merging of accelerometer and gyroscope data
- Activity labeling and metadata tracking
- Comprehensive feature extraction (time and frequency domain)

### Model Implementation
- Custom Gaussian HMM with Baum-Welch training
- Viterbi algorithm for state sequence decoding
- Cross-validation support
- Feature importance analysis

### Results
- **Test Accuracy:** 100%
- **Cross-Validation Accuracy:** 46.7% ± 4.6%
- **Top Discriminative Features:** Low-frequency energy, variance, standard deviation

## Repository Structure

```
Hidden-Markov-Models/
├── data/                              # Processed datasets
│   ├── merged_all_sensors.csv       # Combined sensor data
│   ├── merged_[Activity].csv        # Activity-specific data
│   ├── features_windowed.csv         # Extracted features
│   ├── features_per_recording.csv   # Recording-level features
│   └── hmm_evaluation_metrics.csv   # Model evaluation results
├── Jumping_[session_id]/            # Jumping recordings
├── Standing_[session_id]/           # Standing recordings
├── Still_[session_id]/              # Still recordings
├── Walking_[session_id]/            # Walking recordings
├── merge_datasets.ipynb             # Main implementation notebook
├── hmm_activity_model.pkl          # Trained HMM model
├── Report.md                        # Project report
└── README.md                        # This file
```

## Usage

### Running the Notebook

1. **Open the Jupyter Notebook:**
   ```bash
   jupyter notebook merge_datasets.ipynb
   ```

2. **Execute Cells:** Run all cells in sequence to:
   - Load and preprocess sensor data
   - Extract features using sliding windows
   - Train the HMM model
   - Evaluate performance
   - Visualize results

### Model Loading

```python
import joblib

# Load trained model
model_data = joblib.load('hmm_activity_model.pkl')
hmm_model = model_data['hmm_model']
feature_extractor = model_data['feature_extractor']
label_encoder = model_data['label_encoder']
scaler = model_data['feature_scaler']
```

### Making Predictions

```python
# Extract features from new data
features = feature_extractor.extract_features(new_sensor_data)

# Prepare features
X = features[feature_extractor.feature_names + ['sensor_type']]
X_scaled = scaler.transform(X)

# Predict using Viterbi algorithm
predictions, _ = hmm_model.predict_sequences([X_scaled])
```

## Dependencies

- Python 3.7+
- NumPy
- Pandas
- Matplotlib
- Seaborn
- Scikit-learn
- Scipy
- joblib

Optional:
- hmmlearn (for alternative HMM implementation)

## Report

See `Report.pdf` for comprehensive project documentation including:
- Background and motivation
- Data collection methodology
- Model implementation details
- Results and analysis
- Discussion and future improvements

