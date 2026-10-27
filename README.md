# AI Support Ticket Classifier

**BANKING77 Intent Classification** with Login, Dashboard, Classifier & Chatbot.

```
"My card hasn't arrived yet"
          ↓
   TF-IDF + Logistic Regression
          ↓
     card_arrival · 74%
```

## Features

- **Login system** (session-based, demo accounts)
- **Home dashboard** with stats & quick actions
- **Ticket classifier** – Top-3 predictions + confidence + human-review flag
- **Intent-aware Chatbot** – uses the same NLP model + curated replies
- **Prediction history**
- REST API (`/api/predict`, `/api/chat`, …)
- Clean dark professional UI

## Demo Accounts

| Username | Password  |
|----------|-----------|
| admin    | admin123  |
| agent    | agent123  |
| demo     | demo123   |

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5003**

> Port 5003 is used by default to avoid the common macOS AirPlay conflict on port 5000.

## Project Structure

```
AI_Support_Ticket_Classifier/
├── data/                  # train.csv + test.csv (BANKING77)
├── notebooks/             # training notebook
├── models/                # trained pipeline.joblib
├── app/
│   ├── __init__.py
│   ├── predictor.py
│   ├── chatbot.py         # intent-aware replies
│   ├── routes.py          # login, pages, API
│   └── templates/         # login, home, classify, chatbot, history
├── static/
│   ├── style.css
│   ├── script.js
│   └── chatbot.js
├── config/
├── app.py
├── requirements.txt
└── README.md
```

## Model Performance

| Metric     | Score  |
|------------|--------|
| Accuracy   | 84.2%  |
| Macro F1   | 84.2%  |
| Classes    | 77     |
| Train/Test | 10k / 3k |

## API

```bash
# After login (session cookie) or use the UI
curl -X POST http://127.0.0.1:5003/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Why hasnt my card arrived?"}'
```

Also available: `/api/chat`, `/api/labels`, `/api/metrics`, `/health`

## License

Educational / portfolio use. BANKING77 data retains its original license.
