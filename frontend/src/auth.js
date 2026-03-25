const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

// --- LOGIN & REGISTRATION LOGIC ---

// 1. Called when the user clicks "Continue"
async function checkUserAndLogin() {
    const username = document.getElementById('username-input').value.trim();
    if (!username) {
        showError("Please enter a username.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/user/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username })
        });

        if (response.ok) {
            // SUCCESS: User exists. Log them in!
            const data = await response.json();
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_data', JSON.stringify(data.user));
            
            // Redirect to your main app page (e.g., dashboard.html)
            window.location.href = '/dashboard.html'; 
            
        } else if (response.status === 404) {
            // NOT FOUND: New user. Show the rest of the form.
            document.getElementById('username-section').style.display = 'none';
            document.getElementById('registration-section').style.display = 'block';
        } else {
            showError("An error occurred. Please try again.");
        }
    } catch (error) {
        showError("Could not connect to the server.");
    }
}

// 2. Called when a new user clicks "Register & Login"
async function registerNewUser() {
    const userData = {
        username: document.getElementById('username-input').value.trim(),
        name: document.getElementById('name-input').value.trim(),
        age: parseInt(document.getElementById('age-input').value),
        gender: document.getElementById('gender-select').value,
        height: parseFloat(document.getElementById('height-input').value),
        weight: parseFloat(document.getElementById('weight-input').value),
    };

    // Basic validation
    if (!userData.name || !userData.age || !userData.height || !userData.weight) {
        showError("Please fill out all profile fields.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/user/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_data', JSON.stringify(data.user));
            window.location.href = '/dashboard.html';
        } else if (response.status === 409) {
             showError("Username is already taken. Please go back and try another.");
        } else {
            showError("Registration failed. Please check your details.");
        }
    } catch (error) {
        showError("Could not connect to the server during registration.");
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.innerText = message;
    errorDiv.style.display = 'block';
}
