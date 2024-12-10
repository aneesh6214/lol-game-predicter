import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV

# Load the dataset
df = pd.read_csv("output_files/gold_matchdata.csv")

# Extract target and features
y = df['blue_win'].astype(int)

# Split the champion strings into lists
df['blue_team_list'] = df['blue_team_champs'].apply(lambda x: x.split(','))
df['red_team_list'] = df['red_team_champs'].apply(lambda x: x.split(','))

# Prefix team champs for uniqueness
df['blue_team_list'] = df['blue_team_list'].apply(lambda champs: [f"blue_{c}" for c in champs])
df['red_team_list'] = df['red_team_list'].apply(lambda champs: [f"red_{c}" for c in champs])

# Combine features
df['all_champs'] = df.apply(lambda row: row['blue_team_list'] + row['red_team_list'], axis=1)

# One-hot encode with MultiLabelBinarizer
mlb = MultiLabelBinarizer()
X = mlb.fit_transform(df['all_champs'])

# Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Hyperparameter tuning for Logistic Regression
param_grid = {'C': [0.01, 0.1, 1, 10]}
model = LogisticRegression(max_iter=1000)
grid = GridSearchCV(model, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
grid.fit(X_train, y_train)

best_model = grid.best_estimator_
y_pred = best_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Best C: {grid.best_params_['C']}")
print(f"Test Accuracy after tuning: {acc:.2f}")
