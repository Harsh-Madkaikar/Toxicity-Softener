import os, pickle, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data", "jigsaw_train.csv")
MODELS = os.path.join(BASE, "models")

if not os.path.exists(DATA):
    raise SystemExit("Missing data/jigsaw_train.csv. Download the Jigsaw train.csv first.")

df = pd.read_csv(DATA, usecols=["comment_text", "toxic"]).dropna()
df = df.rename(columns={"comment_text": "text"})
df["text"] = df["text"].astype(str)
df["toxic"] = df["toxic"].astype(int)

# Keep every toxic example and cap clean examples to reduce class imbalance and memory use.
toxic = df[df.toxic == 1]
clean = df[df.toxic == 0]
max_clean = min(len(clean), len(toxic) * 4)
clean = clean.sample(n=max_clean, random_state=42)
df = pd.concat([toxic, clean], ignore_index=True).sample(frac=1, random_state=42)

vectorizer = FeatureUnion([
    ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.99, sublinear_tf=True, max_features=100000, strip_accents="unicode")),
    ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True, max_features=50000))
])
X = vectorizer.fit_transform(df["text"].str.lower())
y = df["toxic"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
model = LogisticRegression(max_iter=1500, class_weight="balanced", C=2.0, solver="liblinear")
model.fit(X_train, y_train)
pred = model.predict(X_test)
print("Training rows:", len(df))
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred, digits=3))
os.makedirs(MODELS, exist_ok=True)
with open(os.path.join(MODELS, "tfidf_vectorizer.pkl"), "wb") as f: pickle.dump(vectorizer, f)
with open(os.path.join(MODELS, "toxicity_model.pkl"), "wb") as f: pickle.dump(model, f)
print("Saved Jigsaw-trained models to", MODELS)
