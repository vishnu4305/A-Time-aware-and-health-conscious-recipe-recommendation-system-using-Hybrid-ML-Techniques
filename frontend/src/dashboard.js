const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

// 1. Check if user is logged in when the page loads
window.onload = function() {
    const userId = localStorage.getItem('user_id');
    const userDataString = localStorage.getItem('user_data');
    
    if (!userId || !userDataString) {
        // Kick them back to login if they aren't authenticated
        window.location.href = 'login.html';
        return;
    }

    // Personalize the welcome message
    const user = JSON.parse(userDataString);
    document.getElementById('welcome-message').innerText = `Welcome back, ${user.name}!`;
};

// 2. Handle Logout
function logout() {
    // Clear the saved user data
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_data');
    
    // Redirect to login page
    window.location.href = 'login.html';
}

// 3. Fetch Recommendations using the logged-in User's ID
async function getRecommendations() {
    const userId = localStorage.getItem('user_id');
    const gammaValue = document.getElementById('gamma-slider').value;
    const grid = document.getElementById('recipes-grid');
    const loader = document.getElementById('loading-spinner');

    // Show loading state, clear old recipes
    grid.innerHTML = '';
    loader.style.display = 'block';

    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                gamma: parseFloat(gammaValue),
                lambda_decay: 2.5,
                top_n: 10
            })
        });

        const data = await response.json();
        loader.style.display = 'none'; // Hide loader

        if (response.ok && data.recommendations) {
            displayRecipes(data.recommendations);
        } else {
            grid.innerHTML = `<div class="alert alert-danger w-100">Failed to load recommendations: ${data.error}</div>`;
        }
    } catch (error) {
        loader.style.display = 'none';
        console.error("Error fetching recipes:", error);
        grid.innerHTML = `<div class="alert alert-danger w-100">Network error. Check console.</div>`;
    }
}

// 4. Display recipes in the HTML grid
function displayRecipes(recipes) {
    const grid = document.getElementById('recipes-grid');
    
    recipes.forEach(recipe => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-header">${recipe.name}</div>
            <div class="card-body">
                <p><strong>Time:</strong> ${recipe.minutes} mins</p>
                <p><strong>Ingredients:</strong> ${recipe.n_ingredients}</p>
                <p><strong>Calories:</strong> ${recipe.calories} kcal</p>
                <hr>
                <div class="small text-muted">${recipe.explanation || ''}</div>
            </div>
        `;
        grid.appendChild(card);
    });
}