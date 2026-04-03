# train_model.py

from dataset import dataset
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle

print("🚀 Loading dataset...")

df = pd.DataFrame(dataset)
df = df.sample(frac=1).reset_index(drop=True)

print("📊 Dataset size:", len(df))
print(df["label"].value_counts())

# Features
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["text"])
y = df["label"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train
print("\n🧠 Training model...")
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("\n📊 Evaluation:")
print(classification_report(y_test, y_pred))

# Save
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("💾 Model saved!")