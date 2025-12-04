## Mental Well-being Agent

This project is a web-based AI agent that:

- **Collects** multiple-choice responses to mental well-being questions from participants (designed for ~200–250 people).
- **Generates** an individual mental well-being profile for each participant using AI analysis.
- **Identifies similar participants** with **≥ 90% matching response patterns** using AI-based similarity detection.
- **Stores profile snapshots** for future comparison and analysis.

### Tech Stack

- **Backend**: FastAPI (Python) with AI-based similarity analysis
- **Frontend**: Single-page HTML + vanilla JavaScript
- **Deployment**: Ready for Render, Railway, Fly.io, Heroku, etc.

---

## 🚀 Quick Public Deployment (Recommended)

**Want anyone to scan QR code and access?** See **[QUICK_START.md](QUICK_START.md)** for 5-minute deployment guide!

### Deploy to Render.com (Free):

1. Push code to GitHub
2. Go to https://render.com
3. Create Web Service → Connect GitHub repo
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn app:app --host=0.0.0.0 --port=$PORT`
6. Get public URL → Generate QR code: `python generate_qr.py YOUR_URL`

**Done!** Anyone can now scan and access from anywhere! 🌍

For detailed instructions, see **[DEPLOYMENT.md](DEPLOYMENT.md)**

---

## 💻 Local Development Setup

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Run the backend server**:

```bash
python app.py
```

The server starts on `http://0.0.0.0:8000` and serves both API and frontend.

3. **Access the app**:
   - Open `http://localhost:8000` in your browser
   - Frontend automatically connects to the backend

### API Overview

- `POST /api/submit`
  - **Body**:
    - `participant_id` (string)
    - `answers` (array of `{ question_id: string, option_value: int }`)
  - **Response**:
    - `participant_id`
    - `profile` (dimensions + text summary)
    - `highly_similar_participants`: list of participants whose response similarity is **≥ 0.9 (90%)**.

- `GET /api/participants`
  - Returns all stored participants, their profiles, and **all pairs** of participants with similarity ≥ 0.9.

- `DELETE /api/reset`
  - Clears all stored participants (for testing/demo).

### AI-Based Similarity Detection

The agent uses **AI-powered analysis** to detect similar mental health patterns:

- **Multi-dimensional feature vectors**: Captures thematic patterns, response intensity, and overall profile
- **Cosine similarity**: Uses machine learning to find semantic similarities beyond exact matches
- **Combined scoring**: 70% AI similarity + 30% exact match ratio
- **Threshold**: Only participants with **≥ 90% similarity** are identified as matches
- **Profile snapshots**: All profiles stored with timestamps for future comparison

When a participant submits responses, they immediately see:
- Their personalized mental well-being profile
- **Alert if similar participants found** (≥90% match) with participant names
- All data displayed in a popup modal

### Features

- ✅ **Public deployment ready** - Deploy once, accessible worldwide
- ✅ **QR code generation** - Easy sharing with participants
- ✅ **AI-based analysis** - Sophisticated pattern matching
- ✅ **Profile snapshots** - Historical data storage
- ✅ **Real-time similarity detection** - Instant matching on submission
- ✅ **Beautiful popup results** - User-friendly result display

### Notes

- Data is stored **in-memory** for simplicity (no database). Restarting the server clears all participants.
- For production with 200+ participants, consider adding a database (PostgreSQL, MongoDB).
- This tool is intended for reflection and pattern discovery and does **not** replace professional mental health care.

### Generate QR Code

After deploying publicly:

```bash
python generate_qr.py https://your-app.onrender.com
```

This creates `qr_code.png` that anyone can scan to access the questionnaire!


