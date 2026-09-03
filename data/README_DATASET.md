# Real-world dataset upgrade (optional, recommended)

The included trained model is ready to run immediately. For stronger real-world coverage, download the original Jigsaw Toxic Comment train.csv and place it here as `data/jigsaw_train.csv`.

Source: Hugging Face mirror of the Jigsaw Toxic Comment Classification Challenge.
Expected columns include `comment_text` and `toxic`.

Then run:

```powershell
python train_jigsaw.py
```

This trains the same TF-IDF + Logistic Regression architecture on real labelled comments and overwrites the model files in `models/`.
