import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score, roc_curve
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# 1. Data Preparation
data = pd.read_csv("output_files/gold_matchdata_fixed.csv")
# Inspect the data for missing values
print("Number of missing values in each column:")
print(data.isnull().sum())

# Handle missing values in 'blue_win'
# Option 1: Remove rows with missing 'blue_win'
data = data.dropna(subset=['blue_win'])

data['blue_win'] = data['blue_win'].astype(int)
data['blue_team_champs'] = data['blue_team_champs'].apply(lambda x: [champ.strip().title() for champ in x.split(',')])
data['red_team_champs'] = data['red_team_champs'].apply(lambda x: [champ.strip().title() for champ in x.split(',')])

# 2. Creating Champion Embeddings
all_matches = data['blue_team_champs'].tolist() + data['red_team_champs'].tolist()
embedding_size = 50
word2vec_model = Word2Vec(sentences=all_matches, vector_size=embedding_size, window=5, min_count=1, workers=4, seed=42)
word2vec_model.save("champion_embeddings.model")

# 3. Feature Engineering
def get_team_embedding(champs, model, embedding_size):
    embeddings = []
    for champ in champs:
        if champ in model.wv:
            embeddings.append(model.wv[champ])
        else:
            embeddings.append(np.zeros(embedding_size))
    if embeddings:
        return np.mean(embeddings, axis=0)
    else:
        return np.zeros(embedding_size)

data['blue_embedding'] = data['blue_team_champs'].apply(lambda champs: get_team_embedding(champs, word2vec_model, embedding_size))
data['red_embedding'] = data['red_team_champs'].apply(lambda champs: get_team_embedding(champs, word2vec_model, embedding_size))

blue_emb_df = pd.DataFrame(data['blue_embedding'].tolist(), columns=[f'blue_emb_{i}' for i in range(embedding_size)])
red_emb_df = pd.DataFrame(data['red_embedding'].tolist(), columns=[f'red_emb_{i}' for i in range(embedding_size)])
X = pd.concat([blue_emb_df, red_emb_df], axis=1)
y = data['blue_win']

# 4. Model Building and Training
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['AUC', 'Accuracy'])

early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

history = model.fit(
    X_train_scaled,
    y_train,
    epochs=100,
    batch_size=32,
    validation_split=0.2,
    callbacks=[early_stop],
    verbose=1
)

# 5. Evaluation
y_pred_proba = model.predict(X_test_scaled).ravel()
y_pred = (y_pred_proba >= 0.5).astype(int)

accuracy = (y_pred == y_test).mean()
roc_auc = roc_auc_score(y_test, y_pred_proba)
f1 = f1_score(y_test, y_pred)

print(f"Accuracy: {accuracy:.4f}")
print(f"ROC-AUC: {roc_auc:.4f}")
print(f"F1 Score: {f1:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

plt.figure(figsize=(8,6))
plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.4f})')
plt.plot([0,1], [0,1], 'k--', label='Random Guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend()
plt.show()

# Training History
plt.figure(figsize=(12,5))

# Loss
plt.subplot(1,2,1)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend()

# AUC
plt.subplot(1,2,2)
plt.plot(history.history['auc'], label='Train AUC')
plt.plot(history.history['val_auc'], label='Validation AUC')
plt.title('Model AUC')
plt.ylabel('AUC')
plt.xlabel('Epoch')
plt.legend()

plt.tight_layout()
plt.show()
