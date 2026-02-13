# ⚡ Quick Start Guide

Get the app running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Node.js 14+ installed
- That's it! (No database installation needed)

## Step-by-Step

### 1. Initialize Database (30 seconds)

```powershell
cd C:\Users\chand\Desktop\Time-aware
python init_database.py
```

**Output**: You should see "✓ Database tables created successfully!"

### 2. Setup Backend (2 minutes)

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies (this takes ~2 minutes)
pip install -r requirements.txt
```

### 3. Setup Frontend (2 minutes)

```powershell
# Open new terminal
cd C:\Users\chand\Desktop\Time-aware\frontend

# Install dependencies
npm install
```

### 4. Test Everything (10 seconds)

```powershell
# In project root
python test_database.py
```

**Expected output**: You should see ✓ marks for connection and user tests.

### 5. Get Sample Data (Optional - for immediate testing)

Create a simple test recipe:

```powershell
# In Python
python
>>> import sqlite3
>>> conn = sqlite3.connect('food_db.sqlite')
>>> conn.execute('''INSERT INTO recipes VALUES 
    (1, 'Test Salad', 'lettuce tomato cucumber', 150, 5.0, 2.0, 25.0, 3.0, 200.0, 12.5, 'Mix all ingredients', '')''')
>>> conn.commit()
>>> conn.close()
>>> exit()
```

### 6. Run the App!

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```

**Browser**: Opens automatically at http://localhost:3000

## 🎉 First Time Using the App

1. **Enter your profile**:
   - Name: "John"
   - Age: 25
   - Height: 180cm
   - Weight: 75kg
   - Select any health conditions
   - Click "Continue to Recommendations"

2. **Adjust sliders**:
   - γ (gamma): 0.5 for balanced
   - λ (lambda): 2.5 for moderate time decay

3. **Get Recommendations**:
   - Click "Get Personalized Recommendations"
   - (You'll see "No recommendations" if database is empty - that's expected!)

## 📥 Loading Full Dataset

To get actual recommendations, you need the Kaggle dataset:

### Download Data (5 minutes)

1. Go to: https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
2. Download the dataset
3. Extract `RAW_recipes.csv` and `RAW_interactions.csv`
4. Place them in: `C:\Users\chand\Desktop\Time-aware\data\`

### Process Data (10-15 minutes)

```powershell
cd data
python preprocess.py
python load_db.py
```

**This creates your full database with 180k recipes!**

### Restart Backend

```powershell
cd backend
python app.py
```

Now you'll get real recommendations! 🎊

## 🆘 Common Issues

### "Module not found"
**Fix**: Make sure venv is activated (you should see `(venv)` in your prompt)

### "Port already in use"
**Fix**: Close other instances of the app

### "Database locked"
**Fix**: Close all programs, then restart the backend

### "No recommendations found"
**Fix**: Load the full dataset (see above)

## 📱 Mobile Testing

The app works on mobile! On same WiFi network:

1. Find your IP: `ipconfig` (look for IPv4 Address)
2. Open on phone: `http://YOUR_IP:3000`

## ⏭️ Next Steps

- [README.md](README.md) - Full project documentation
- [SQLITE_GUIDE.md](SQLITE_GUIDE.md) - Database details
- [SQLITE_MIGRATION.md](SQLITE_MIGRATION.md) - What changed from MySQL

## 🎯 You're Ready!

Your Time-Aware Recipe Recommender is up and running!

Have fun exploring personalized recipe recommendations! 🍽️
