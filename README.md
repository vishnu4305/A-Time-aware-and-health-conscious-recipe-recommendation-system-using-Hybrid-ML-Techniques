# Time-Aware Health-Conscious Recipe Recommendation System

A multi-user, cloud-deployed web application that provides personalized recipe recommendations by balancing **taste preferences** with **health requirements** using machine learning.

## 🚀 Key Features

- **Time-Aware Collaborative Filtering**: Recent ratings weighted more heavily (based on Rostami et al., 2023).
- **Content-Based Filtering**: Semantic ingredient similarity using HuggingFace Sentence-Transformers.
- **Health-Conscious Scoring**: WHO nutritional guidelines + obesity/diabetes management.
- **Daily Meal Planner**: Organized breakfast, lunch, snacks, and dinner recommendations with calorie distribution.
- **User Control**: Adjustable γ (taste vs health) and λ (time decay) sliders.
- **Persistent Sessions**: React-based seamless authentication flow.
- **Cloud Optimized**: Dynamic memory scaling to prevent Out-Of-Memory (OOM) crashes on Free Tier cloud hosts.

## 🔄 How It Works (Step-by-Step Workflow)

1. **User Profiling**: Users register by entering their physical metrics (Age, Height, Weight, Gender, Activity Level) and tagging any health conditions (e.g., Diabetes, Obesity).
2. **Health Baseline Calculation**: The backend calculates the user's Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE). If the user is flagged for obesity management, it enforces a strict 500 kcal daily deficit.
3. **Taste Preference Learning**: As the user interacts with the system, the AI builds a preference profile using two methods:
   - *Content-Based Filtering*: HuggingFace Sentence-Transformers read the actual ingredients to learn flavor profiles the user enjoys.
   - *Time-Aware Collaborative Filtering*: The algorithm finds similar users but applies a mathematical decay (Lambda λ) to give higher weight to *recently* rated items, adapting to changing tastes over time.
4. **Nutritional Health Scoring**: Every recipe in the database is graded against World Health Organization (WHO) macro guidelines (10-15% Protein, 15-30% Fat, 55-75% Carbs). It also penalizes recipes if they violate user conditions (e.g., high glycemic load or >10g sugar for diabetics).
5. **Hybrid Recommendation Generation**: The engine calculates a Final Score by fusing the Taste prediction and the Health score based on the user's Gamma (γ) slider.
   - `γ = 0.0`: Pure comfort food (Taste only).
   - `γ = 0.5`: Balanced recommendation.
   - `γ = 1.0`: Pure strict diet (Health only).
6. **Daily Meal Planning**: To build a meal plan, the system uses NLP to semantically classify the highest-scoring recipes into Breakfast, Lunch, Snacks, and Dinner, ensuring the combination perfectly hits the user's custom calorie distribution for the day.

## � Tech Stack

- **Frontend**: React.js, React Router, React Bootstrap (Hosted on **Vercel**)
- **Backend**: Python Flask, Gunicorn (Hosted on **Render**)
- **Database**: MongoDB Atlas (Cloud) / SQLite (Offline Local Support)
- **Machine Learning**: PyTorch, Sentence-Transformers, scikit-learn, Pandas, NumPy
- **Data Storage**: Google Drive (for hosting the massive 356MB pre-computed embeddings file)

## 📁 Project Structure

```
Time-aware/
├── data/                    # Kaggle Dataset & preprocessing scripts
├── frontend/                # React application (Deployed to Vercel)
│   ├── src/
│   │   ├── components/      # UserProfile, Dashboard, ProfilePage
│   │   ├── App.js           # Main routing and auth state
│   │   └── index.css        # Custom UI styling
├── backend/                 # Flask API server (Deployed to Render)
│   ├── app.py               # REST API Endpoints
│   ├── database.py          # MongoDB Atlas connection & queries
│   └── requirements.txt     # Python dependencies
├── ml_models/               # Machine learning logic
│   ├── recommender.py       # Hybrid Recommendation Engine
│   ├── embeddings/          # Lazy-loaded/On-the-fly generated embeddings
│   └── meal_planner.py      # Calorie distribution logic
└── README.md
```

## ☁️ Cloud Deployment Instructions

This project is designed to be hosted seamlessly on the cloud.

### 1. Database Setup (MongoDB Atlas)
1. Create a free cluster on MongoDB Atlas.
2. Under Network Access, allow access from anywhere (`0.0.0.0/0`).
3. Get your connection string (`mongodb+srv://...`).

### 2. Backend Deployment (Render)
1. Connect your GitHub repository to Render and create a **Web Service**.
2. **Configuration**:
   - **Root Directory**: `(Leave Blank / Empty)`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn --chdir backend app:app`
3. **Environment Variables**:
   - `MONGO_URI`: Your MongoDB Atlas Connection String
   - `PYTHON_VERSION`: `3.9.0`
   - `RENDER`: `true` *(This tells the app to use memory-saving techniques)*

### 3. Frontend Deployment (Vercel)
1. Push your code to GitHub and connect it to Vercel.
2. Vercel will automatically detect the React app in the `frontend` folder.
3. **Connecting the Frontend to Backend**: In your React components (e.g., `App.js`, `Dashboard.jsx`), ensure the `API_BASE_URL` points to your live Render URL:
   ```javascript
   const API_BASE_URL = 'https://your-render-app-name.onrender.com';
   ```
4. Deploy the Vercel app.

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.8+
- Node.js 14+

### 1. Backend Setup
```bash
cd backend
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set local environment variables
set MONGO_URI="your_mongodb_connection_string"

# Run the server
python app.py
```
*Backend will run on `http://localhost:5000`*

### 2. Frontend Setup
```bash
cd frontend
npm install

# Temporarily change API_BASE_URL in your React files to http://localhost:5000 for local testing

npm start
```
*Frontend will run on `http://localhost:3000`*

## 🧠 Algorithm Overview

### Final Score Formula
```text
final_score = (1-γ) × preference + γ × health
preference = 0.6 × collaborative_filtering + 0.4 × content_based
```

### Time-Aware Collaborative Filtering
```text
Time Weight (TW) = exp(-λ × (TP - t_ui)) + exp(-λ × (TP - t_uj))
```

### Memory Management (Render Free Tier)
To prevent Out-Of-Memory (OOM) crashes on 512MB RAM cloud hosts:
1. The background data-loading thread is disabled.
2. Data is "lazy-loaded" (only fetched upon the first user request).
3. Instead of downloading a massive 356MB pre-computed `.npy` file, the backend dynamically pulls a subset of recipes (500 limit) and generates PyTorch embeddings **on-the-fly**.

## 🔌 API Endpoints

### Authentication & Users
- `POST /user/login` - Authenticate returning user
- `POST /user/create` - Register new user
- `PUT /user/update/<user_id>` - Update user metrics (weight, age, etc.)

### Recommendations
- `POST /recommend` - Get AI recipe recommendations (Hybrid CF + CBF)
- `POST /recommend/meal-plan` - Get calorie-distributed daily meal plan

### Recipes & Health
- `GET /health` - API Health check
- `GET /debug/db` - Database connectivity diagnostic

## ⚠️ Troubleshooting

**1. Blank White Page on Frontend**
- **Cause**: Mixing React Router with hard `window.location.href` redirects to `.html` files.
- **Fix**: Ensure all routing is handled via `react-router-dom` (`<Navigate />` or `useNavigate()`) between React `.jsx` components.

**2. Render Deployment Fails (ModuleNotFoundError: pymongo)**
- **Cause**: Using MongoDB Atlas (`mongodb+srv://`) requires an extra DNS package.
- **Fix**: Ensure `pymongo[srv]==4.6.1` is in your `backend/requirements.txt`, clear the Render build cache, and redeploy.

**3. Render "OOMKilled" or "Port scan timeout"**
- **Cause**: Loading 350MB+ of ML data into RAM instantly exceeds Render's 512MB Free Tier limit.
- **Fix**: Ensure `is_render` flags are active in `recommender.py` to utilize on-the-fly embedding generation instead of massive file downloads.

## 📚 References
- Rostami et al. (2023) - Time-Aware Collaborative Filtering
- WHO Nutritional Guidelines
- Food.com Dataset (Kaggle)
- HuggingFace Sentence-Transformers (all-MiniLM-L6-v2)