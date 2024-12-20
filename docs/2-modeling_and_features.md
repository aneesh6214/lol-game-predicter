# Modeling & Feature Engineering (Step 2)

## Overview
This phase aims to transform the raw match data into a format suitable for machine learning models. Build and evaluate multiple models and compare performance.

## Iteration 1: Logistic Regression Model

### Goal
- Transform raw champion draft data into numerical features.
- Apply a simple logistic regression model to predict match outcomes.

### Training Data
- 20K Rows, Sample:
```
match_id       | blue_team_champs                     | red_team_champs                             | blue_win
NA1_5121379795 | "Kayle,JarvanIV,Garen,Smolder,Senna" | "Mordekaiser,Darius,Belveth,Seraphine,Nami" | False
NA1_5124368116 | "Garen,Gragas,Ryze,Caitlyn,Leona"    |  "Briar,Lillia,Zed,Jhin,Senna"              | True
```

### Feature Engineering
- **Champion Encoding:**
  - Used **MultiLabelBinarizer** to convert lists of champions into a binary matrix.
  - Each column represents a unique champion-team combination (e.g., `blue_Garen`, `red_Thresh`).
  - This resulted in a feature set where each match is represented by multiple binary indicators.

### Model Selection
- **Chosen Algorithm:** Logistic Regression
  - Selected for its simplicity and ability to provide a quick baseline.
  - Suitable for binary classification (win/loss prediction).

### Hyperparameter Tuning
- **Parameter Tuned:** Regularization strength (`C`)
  - Explored different values of `C` to find the optimal balance between bias and variance.
  - Conducted a grid search over a range of `C` values (e.g., 0.01, 0.1, 1, 10).

### Results
- **Accuracy:** ~52%
  - Slight improvement over random guessing (50%).
  - Indicates that champion picks alone offer limited predictive power with the current feature set.

### Observations
- **Model Performance:** 
  - The logistic regression model struggled to capture the complex interactions between champions.
  - Possible overfitting or underfitting due to the high dimensionality of the feature space.

### Next Steps
1. **Advanced Feature Engineering:**
   - Incorporate champion roles and synergies.
   - Include additional features such as player statistics or match duration.
2. **Model Exploration:**
   - Experiment with more complex algorithms (e.g., Random Forest, Gradient Boosting).
   - Utilize ensemble methods to improve predictive performance.
3. **Data Augmentation:**
   - Increase dataset size beyond 20,000 rows for better generalization.
   - Ensure diverse champion combinations to enhance model learning.

## Summary
The initial logistic regression model provided a baseline accuracy of 52%. While this is a modest improvement, it highlights the need for more sophisticated feature engineering and potentially more complex models to effectively predict match outcomes based on champion selections.

