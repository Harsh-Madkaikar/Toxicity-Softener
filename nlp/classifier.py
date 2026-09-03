import os, pickle, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "toxicity_dataset_large.csv")
MODELS = os.path.join(BASE, "models")
os.makedirs(MODELS, exist_ok=True)

df = pd.read_csv(DATA).dropna(subset=["text", "toxic"])
df["text"] = df["text"].astype(str)
y = df["toxic"].astype(int)

vectorizer = FeatureUnion([
    ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.98, sublinear_tf=True, max_features=70000, strip_accents="unicode")),
    ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True, max_features=50000))
])
X = vectorizer.fit_transform(df["text"].str.lower())
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
model = LogisticRegression(max_iter=1500, class_weight="balanced", C=2.0, solver="liblinear")
model.fit(X_train, y_train)
pred = model.predict(X_test)
print("Rows:", len(df))
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred, digits=3))
with open(os.path.join(MODELS, "tfidf_vectorizer.pkl"), "wb") as f: pickle.dump(vectorizer, f)
with open(os.path.join(MODELS, "toxicity_model.pkl"), "wb") as f: pickle.dump(model, f)
print("Saved models to", MODELS)
