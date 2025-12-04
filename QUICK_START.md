# 🚀 Quick Start - Public Deployment

**कोई भी user scan करके access कर सके - यह setup करें!**

## सबसे आसान तरीका (Render.com) - 5 मिनट में!

### Step 1: GitHub पर Code Push करें

```bash
# अगर git repo नहीं है
git init
git add .
git commit -m "Mental Well-being Agent"

# GitHub पर नया repo बनाएं, फिर:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Render.com पर Deploy करें

1. **https://render.com** पर जाएं
2. **"New +"** → **"Web Service"** click करें
3. GitHub account connect करें
4. अपना repository select करें
5. Settings fill करें:
   - **Name**: `mental-wellbeing-agent`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host=0.0.0.0 --port=$PORT`
6. **"Create Web Service"** click करें
7. 2-3 मिनट wait करें

### Step 3: QR Code Generate करें

Render आपको एक URL देगा जैसे: `https://mental-wellbeing-agent.onrender.com`

```bash
python generate_qr.py https://mental-wellbeing-agent.onrender.com
```

### Step 4: QR Code Share करें! 🎉

अब `qr_code.png` को:
- Print करें
- Screen पर display करें  
- Social media पर share करें
- **कोई भी scan करके access कर सकता है!** 🌍

---

## ✅ Test करें

1. Phone से QR code scan करें
2. Questionnaire open होगा
3. Questions answer करें
4. Submit करें
5. Mental health profile देखें!

---

## 🔧 Alternative: Railway.app

**Important:** `runtime.txt` file को delete कर दें (Railway auto-detect करता है)

1. **https://railway.app** पर जाएं
2. GitHub से login करें
3. "New Project" → "Deploy from GitHub"
4. Repository select करें
5. Railway automatically:
   - Python version detect करेगा
   - Dependencies install करेगा
   - App start करेगा
6. URL मिलेगा → QR code generate करें

**Note:** अगर error आए तो Railway dashboard में:
- Settings → Build Command: `pip install -r requirements.txt`
- Settings → Start Command: `uvicorn app:app --host=0.0.0.0 --port=$PORT`

---

## ❓ Problem?

- **QR code नहीं बन रहा?** → `pip install qrcode[pil]`
- **Deploy नहीं हो रहा?** → Render logs check करें
- **URL काम नहीं कर रहा?** → 2-3 मिनट wait करें (first deploy में time लगता है)

---

## 📱 Ready!

अब आपका app **publicly accessible** है! कोई भी दुनिया में कहीं से भी scan करके access कर सकता है! 🎉

