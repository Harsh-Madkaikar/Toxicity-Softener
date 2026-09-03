# Toxicity Softener — final stable build

## Folder structure

- `backend/app.py` — Flask API
- `nlp/pipeline.py` — prediction + positive safeguard
- `nlp/softener.py` — variable/context-aware rewrites
- `nlp/preprocess.py` — text preprocessing
- `nlp/classifier.py` — trains the TF-IDF + Logistic Regression model
- `data/toxicity_dataset_large.csv` — larger balanced starter dataset
- `extension/` — Chrome extension (Gmail, WhatsApp Web, Instagram)
- `models/` — generated model files

## 1. Install

From the project root in PowerShell:

```powershell
python -m pip install -r requirements.txt
```

## 2. Train the model

```powershell
python train.py
```

This regenerates the larger dataset and creates:
- `models/tfidf_vectorizer.pkl`
- `models/toxicity_model.pkl`

## 3. Start the backend

```powershell
python backend/app.py
```

Keep this terminal running. You should see:
`Toxicity Softener API running at http://127.0.0.1:5000`

## 4. Load the extension

Chrome/Edge → `chrome://extensions` → Developer mode → **Load unpacked** → select the **extension** folder.

After every code change: click **Reload** on the extension, then refresh Gmail/WhatsApp/Instagram.

## Important

The content script **never calls localhost directly**. It sends the text to the Manifest V3 service worker, and the service worker calls Flask. This avoids the page-origin CORS problem visible in the earlier console logs.

Do not keep an older copy of `content.js` or another version of the extension loaded at the same time.

## Use on other laptops / online deployment

The extension can be hosted against a public HTTPS Flask API so users do not need Python or the backend installed locally. This project includes `render.yaml` and `Procfile` for Render deployment.

1. Push the project to a GitHub repository.
2. In Render, create a Web Service from that repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn backend.app:app`
5. After deployment, copy the HTTPS service URL.
6. Replace `API_URL` in `extension/background.js` with `<your-service-url>/analyze`.
7. Add the same HTTPS API origin to `host_permissions` in `extension/manifest.json`.
8. Reload the unpacked extension.

The API listens on `0.0.0.0` and respects Render's `PORT` environment variable.
