const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

// 1. Load user data when the page opens
window.onload = function() {
    const savedData = localStorage.getItem('user_data');
    if (savedData) {
        const user = JSON.parse(savedData);
        
        // Pre-fill the form fields with existing data
        document.getElementById('update-name').value = user.name || '';
        document.getElementById('update-age').value = user.age || '';
        document.getElementById('update-gender').value = user.gender || 'male';
        document.getElementById('update-height').value = user.height || '';
        document.getElementById('update-weight').value = user.weight || '';
    } else {
        alert("You are not logged in!");
        window.location.href = 'login.html'; // Kick them back to login if they bypassed it
    }
};

// 2. Update profile when "Save Changes" is clicked
async function updateProfile() {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
        alert("Error: Not logged in.");
        window.location.href = 'login.html';
        return;
    }

    const successMsg = document.getElementById('update-success-message');
    const errorMsg = document.getElementById('update-error-message');
    successMsg.style.display = 'none';
    errorMsg.style.display = 'none';

    // Gather the newly updated data from the form
    const updatedData = {
        name: document.getElementById('update-name').value.trim(),
        age: parseInt(document.getElementById('update-age').value),
        gender: document.getElementById('update-gender').value,
        height: parseFloat(document.getElementById('update-height').value),
        weight: parseFloat(document.getElementById('update-weight').value),
        activity_level: 1.2, // Standard default, or pull from existing user_data
        conditions: []       // Standard default, or pull from existing user_data
    };

    if (!updatedData.name || !updatedData.age || !updatedData.height || !updatedData.weight) {
        errorMsg.innerText = "Please fill out all fields.";
        errorMsg.style.display = 'block';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/user/update/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        });

        if (response.ok) {
            const data = await response.json();
            
            // Update local storage so the rest of the app uses the new weight/height
            localStorage.setItem('user_data', JSON.stringify(data.user));
            
            successMsg.innerText = "Profile updated successfully!";
            successMsg.style.display = 'block';
        } else {
            errorMsg.innerText = "Failed to update profile. Please try again.";
            errorMsg.style.display = 'block';
        }
    } catch (error) {
        console.error("Update Error:", error);
        errorMsg.innerText = "Could not connect to the server.";
        errorMsg.style.display = 'block';
    }
}