import os, pickle, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "toxicity_dataset_large.csv")
MODELS = os.path.join(BASE, "models")
os.makedirs(MODELS, exist_ok=True)

df = pd.read_csv(DATA).dropna(subset=["text", "toxic"])
df["text"] = df["text"].astype(str)
y = df["toxic"].astype(int)

# Word + character features make the model much more tolerant of spelling,
# punctuation, short social-media text, and unseen wording.
vectorizer = TfidfVectorizer(
    analyzer="word", ngram_range=(1, 2), min_df=2, max_df=0.98,
    sublinear_tf=True, max_features=60000, strip_accents="unicode"
)
X = vectorizer.fit_transform(df["text"].str.lower())

with open(os.path.join(MODELS, "tfidf_vectorizer.pkl"), "wb") as f:
    pickle.dump(vectorizer, f)

print(f"TF-IDF trained on {len(df):,} rows; features: {X.shape[1]:,}")
