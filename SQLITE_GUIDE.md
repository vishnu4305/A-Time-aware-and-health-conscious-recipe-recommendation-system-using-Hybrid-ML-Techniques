# SQLite Setup Guide - No Installation Required!

## ✅ Advantages of SQLite for This Project

1. **Zero Installation** - Comes built-in with Python
2. **Portable** - Single file database that travels with your project
3. **Easy Sharing** - Just copy the `.sqlite` file
4. **Perfect for College** - No server setup, works on any machine
5. **No Configuration** - Works out of the box

## 📁 Database File Location

Your database is stored as: `food_db.sqlite` in the project root directory.

This single file contains:
- All recipes (180k+)
- All ratings (700k+)
- All user profiles

## 🚀 Quick Start

### First Time Setup

```powershell
# 1. Activate virtual environment
cd backend
.\venv\Scripts\Activate.ps1

# 2. Process data (creates database automatically)
cd ../data
python preprocess.py
python load_db.py

# 3. Done! food_db.sqlite is now created
```

### Running the App

```powershell
# Backend (make sure venv is activated)
cd backend
python app.py

# Frontend (separate terminal)
cd frontend
npm start
```

## 📤 Sharing With Others

### Option 1: Share Everything (Easiest)

1. Copy your entire project folder
2. Other users just need to:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   
   cd ../frontend
   npm install
   ```
3. They run the app - **no database setup needed!**

### Option 2: Share Without Database (Smaller)

1. Don't include `food_db.sqlite` in your share
2. Provide them with:
   - Instructions to download dataset from Kaggle
   - Run `preprocess.py` and `load_db.py`

## 🔍 Viewing Your Database

You can open and browse `food_db.sqlite` using:

1. **DB Browser for SQLite** (Free)
   - Download: https://sqlitebrowser.org/
   - Open `food_db.sqlite` to view all tables

2. **VS Code Extension**
   - Install "SQLite Viewer" extension
   - Click on `food_db.sqlite` to browse

3. **Python**
   ```python
   import sqlite3
   conn = sqlite3.connect('food_db.sqlite')
   cursor = conn.cursor()
   cursor.execute("SELECT COUNT(*) FROM recipes")
   print(cursor.fetchone())  # Number of recipes
   ```

## ⚠️ Important Notes

### Database File Size
- Empty: ~100KB
- With full dataset: ~500MB-1GB
- This is normal and expected!

### Backup Your Database
```powershell
# Create backup
copy food_db.sqlite food_db_backup.sqlite

# Or use git
git add food_db.sqlite
git commit -m "Database with full dataset"
```

### Reset Database
```powershell
# Delete existing database
rm food_db.sqlite

# Recreate from scratch
cd data
python load_db.py
```

## 🆚 SQLite vs MySQL Comparison

| Feature | SQLite (Current) | MySQL (Previous) |
|---------|------------------|------------------|
| Installation | None needed | Requires MySQL server |
| Setup | Automatic | Manual configuration |
| Portability | Single file | Server-dependent |
| Sharing | Copy file | Each user sets up server |
| Performance | Fast for <1M rows | Faster for massive datasets |
| College Demo | ✅ Perfect | ❌ Complex setup |

## 🔧 Troubleshooting

### "Database is locked"
- Close all programs accessing the database
- Only one write operation at a time

### "File not found"
- Check `.env` file: `DATABASE_PATH=../food_db.sqlite`
- Make sure you're in the right directory

### "Table doesn't exist"
- Run `python load_db.py` to create tables
- Check if `database.sql` was executed

## 📚 Learn More

- SQLite Official: https://www.sqlite.org/
- Python sqlite3 module: https://docs.python.org/3/library/sqlite3.html
