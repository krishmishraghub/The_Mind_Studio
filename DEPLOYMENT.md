# Deployment Guide - Mental Well-being Agent

This guide will help you deploy the Mental Well-being Agent publicly so **anyone can scan the QR code and access it from anywhere**.

## 🚀 Quick Public Deployment (Recommended)

### Option 1: Render.com (Easiest - Free Tier Available) ⭐

**Step 1: Create Account**
- Go to https://render.com
- Sign up with GitHub (recommended) or email

**Step 2: Create New Web Service**
1. Click "New +" → "Web Service"
2. Connect your GitHub repository (or push this code to GitHub first)
3. Select your repository

**Step 3: Configure Settings**
- **Name**: `mental-wellbeing-agent` (or any name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host=0.0.0.0 --port=$PORT`
- **Plan**: Free (or paid for better performance)

**Step 4: Deploy**
- Click "Create Web Service"
- Wait 2-3 minutes for deployment
- You'll get a URL like: `https://mental-wellbeing-agent.onrender.com`

**Step 5: Generate QR Code**
```bash
python generate_qr.py https://mental-wellbeing-agent.onrender.com
```

**Done!** 🎉 Anyone can now scan the QR code and access your questionnaire from anywhere in the world!

---

### Option 2: Railway.app (Also Free & Easy)

**Step 1: Remove runtime.txt (Important!)**
- Railway doesn't need `runtime.txt` - it auto-detects Python
- Delete `runtime.txt` file if it exists (it can cause `mise` errors)

**Step 2: Create Account**
- Go to https://railway.app
- Sign up with GitHub

**Step 3: Deploy**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway auto-detects Python and deploys

**Step 4: Configure (if needed)**
If auto-detection doesn't work, go to Settings:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host=0.0.0.0 --port=$PORT`

**Step 5: Get URL**
- Railway provides a URL like: `https://your-app.up.railway.app`
- Generate QR code: `python generate_qr.py https://your-app.up.railway.app`

---

### Option 3: Fly.io (Free Tier)

**Step 1: Install Fly CLI**
```bash
# macOS
brew install flyctl

# Or download from https://fly.io/docs/hands-on/install-flyctl/
```

**Step 2: Login & Deploy**
```bash
flyctl auth login
flyctl launch
```

**Step 3: Get URL & Generate QR Code**
- Fly.io provides a URL
- Generate QR: `python generate_qr.py https://your-app.fly.dev`

---

## 📱 After Deployment - Generate QR Code

Once you have your public URL (e.g., `https://your-app.onrender.com`):

```bash
python generate_qr.py https://your-app.onrender.com
```

This creates `qr_code.png` that you can:
- Print on posters/flyers
- Display on screens/projectors
- Share digitally
- **Anyone can scan it from anywhere!**

---

## 🔧 Local Testing (Optional - Before Public Deployment)

## 📋 Step-by-Step: Render Deployment (Detailed)

### Prerequisites
1. **GitHub Account** (free)
2. **Git installed** on your computer

### Detailed Steps:

**1. Push Code to GitHub**
```bash
# If not already a git repo
git init
git add .
git commit -m "Initial commit"
git branch -M main

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

**2. Deploy on Render**
- Go to https://render.com
- Click "New +" → "Web Service"
- Connect GitHub account
- Select your repository
- Fill in:
  - **Name**: `mental-wellbeing-agent`
  - **Environment**: `Python 3`
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn app:app --host=0.0.0.0 --port=$PORT`
- Click "Create Web Service"
- Wait 2-3 minutes

**3. Get Your Public URL**
- Render gives you: `https://mental-wellbeing-agent.onrender.com`
- Copy this URL

**4. Generate QR Code**
```bash
python generate_qr.py https://mental-wellbeing-agent.onrender.com
```

**5. Share QR Code**
- Print it, display it, share it!
- Anyone can scan and access from anywhere 🌍

---

## ✅ Backend Already Configured for Production

The backend (`app.py`) is already configured to:
- ✅ Use `PORT` environment variable (auto-set by cloud platforms)
- ✅ Serve frontend static files
- ✅ Handle CORS for public access
- ✅ Work with any deployment platform

**No changes needed!** Just deploy and it works! 🎉

---

## 🌐 Frontend Access

Once deployed publicly, your frontend is accessible at:
- **Main URL**: `https://your-app.onrender.com/` (root)
- **Direct**: `https://your-app.onrender.com/static/index.html`

The frontend **automatically detects the API URL**, so it works perfectly in production!

**Users can:**
1. Scan QR code → Opens questionnaire
2. Answer questions
3. Submit → Get mental health profile
4. See similar participants (if ≥90% match)

---

## Testing the Deployment

1. **Test locally first:**
   ```bash
   python app.py
   ```
   Visit `http://localhost:8000` in your browser

2. **Test from mobile device:**
   - Connect phone to same WiFi network
   - Scan QR code or visit `http://YOUR_LOCAL_IP:8000`
   - Submit a test response

3. **Check API endpoints:**
   - `http://your-domain.com/api/participants` - View all participants
   - `http://your-domain.com/api/snapshots` - View all profile snapshots
   - `http://your-domain.com/api/debug/similarity/id1/id2` - Test similarity

---

## Security Considerations

For production deployment with sensitive mental health data:

1. **Add Authentication** (recommended):
   - Implement API keys or user authentication
   - Protect admin endpoints (`/api/participants`, `/api/reset`)

2. **Use HTTPS:**
   - Most deployment platforms (Render, Railway, Heroku) provide HTTPS by default
   - For local deployment, consider using ngrok for HTTPS tunnel

3. **Data Storage:**
   - Current implementation uses in-memory storage
   - For production, consider adding database (PostgreSQL, MongoDB)
   - Update `app.py` to persist data

4. **Rate Limiting:**
   - Add rate limiting to prevent abuse
   - Use `slowapi` or similar library

---

## 🎯 Quick Deployment Checklist

- [ ] Push code to GitHub
- [ ] Create account on Render/Railway/Fly.io
- [ ] Deploy web service
- [ ] Get public URL (HTTPS)
- [ ] Generate QR code: `python generate_qr.py YOUR_URL`
- [ ] Test by scanning QR code on phone
- [ ] Share QR code with participants!

**That's it!** Your app is now accessible worldwide! 🌍

---

## Troubleshooting

### QR Code Not Working
- Ensure the URL is accessible from the device scanning
- Check firewall settings if using local network
- Verify the backend server is running

### CORS Errors
- Backend already configured with CORS middleware
- If issues persist, check `allow_origins` in `app.py`

### Port Already in Use
- Change port in `app.py`: `uvicorn.run("app:app", host="0.0.0.0", port=8001)`
- Update QR code with new port

### Participants Not Seeing Similar Matches
- Check backend console logs for similarity scores
- Use debug endpoint: `/api/debug/similarity/id1/id2`
- Ensure both participants have submitted responses

---

## Support

For issues or questions:
1. Check backend console logs
2. Test API endpoints directly
3. Verify all dependencies are installed
4. Ensure Python 3.8+ is being used

