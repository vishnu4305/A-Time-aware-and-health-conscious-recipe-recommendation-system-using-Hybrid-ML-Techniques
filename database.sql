-- Time-Aware Recipe Recommendation System Database Schema
-- SQLite Version

-- Users table: stores user profiles and health conditions
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    height REAL NOT NULL,  -- in cm
    weight REAL NOT NULL,  -- in kg
    activity_level REAL DEFAULT 1.2,  -- 1.2=sedentary, 1.55=moderate, 1.9=active
    conditions TEXT,  -- JSON string e.g., ["obesity", "diabetes"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);

-- Recipes table: stores recipe details and nutritional information
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    ingredients TEXT,
    calories INTEGER,
    protein REAL,
    fat REAL,
    carbs REAL,
    sugar REAL,
    sodium REAL,
    gl REAL,  -- Glycemic Load (precomputed)
    steps TEXT,
    image_url TEXT
);

CREATE INDEX IF NOT EXISTS idx_recipes_calories ON recipes(calories);
CREATE INDEX IF NOT EXISTS idx_recipes_sugar ON recipes(sugar);

-- Ratings table: stores user ratings with timestamps for time-aware recommendations
CREATE TABLE IF NOT EXISTS ratings (
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    timestamp TIMESTAMP NOT NULL,
    month_index INTEGER,  -- Precomputed time period for time-aware algorithm
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ratings_user_timestamp ON ratings(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_ratings_month_index ON ratings(month_index);
