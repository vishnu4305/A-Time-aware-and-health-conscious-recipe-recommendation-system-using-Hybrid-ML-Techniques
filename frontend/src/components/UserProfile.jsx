import React, { useState } from 'react';
import { Card, Form, Button, Alert, Row, Col, Container } from 'react-bootstrap';

const RENDER_URL = process.env.REACT_APP_API_URL || 'https://recipe-recommender-api-57hq.onrender.com';
const LOCAL_URL = 'http://localhost:5000';
let workingUrl = RENDER_URL;

// Helper to automatically fallback to localhost if Render is asleep or fails
const safeFetch = async (endpoint, options) => {
    try {
        const response = await fetch(`${workingUrl}${endpoint}`, options);
        if (response.status >= 500 && workingUrl !== LOCAL_URL) {
            console.warn(`Cloud backend returned ${response.status}. Falling back to ${LOCAL_URL}...`);
            workingUrl = LOCAL_URL;
            return await fetch(`${workingUrl}${endpoint}`, options);
        }
        return response;
    } catch (err) {
        if (workingUrl !== LOCAL_URL) {
            console.warn(`Cloud backend offline. Falling back to local server at ${LOCAL_URL}...`);
            workingUrl = LOCAL_URL;
            return await fetch(`${workingUrl}${endpoint}`, options);
        }
        throw err;
    }
};

function UserProfile({ onUserCreated }) {
    const [username, setUsername] = useState('');
    const [isNewUser, setIsNewUser] = useState(false);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    // Full profile states
    const [name, setName] = useState('');
    const [age, setAge] = useState('');
    const [height, setHeight] = useState('');
    const [weight, setWeight] = useState('');
    const [gender, setGender] = useState('male');
    const [activityLevel, setActivityLevel] = useState('1.2');
    const [conditions, setConditions] = useState([]);

    const handleConditionChange = (condition) => {
        setConditions(prev => 
            prev.includes(condition) 
                ? prev.filter(c => c !== condition)
                : [...prev, condition]
        );
    };

    // Step 1: Handle checking the username
    const handleUsernameSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const response = await safeFetch('/user/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username })
            });

            if (response.ok) {
                const data = await response.json();
                onUserCreated(data.user); // This tells App.js the user is logged in
            } else if (response.status === 404) {
                // User not found, show the rest of the form
                setIsNewUser(true);
            } else {
                setError("An error occurred. Please try again.");
            }
        } catch (err) {
            setError("Could not connect to the server.");
        } finally {
            setLoading(false);
        }
    };

    // Step 2: Handle full registration
    const handleRegistrationSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        const userData = { 
            username, 
            name, 
            age: parseInt(age), 
            height: parseFloat(height), 
            weight: parseFloat(weight), 
            gender,
            activity_level: parseFloat(activityLevel),
            conditions 
        };

        try {
            const response = await safeFetch('/user/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                const data = await response.json();
                onUserCreated(data.user); // Log them in!
            } else if (response.status === 409) {
                setError("Username is already taken.");
            } else {
                setError("Registration failed. Please check your details.");
            }
        } catch (err) {
            setError("Could not connect to the server.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container className="d-flex justify-content-center mt-5">
            <Card style={{ width: '600px' }}>
                <Card.Body>
                    <h4 className="text-center mb-2">👤 User Profile</h4>
                    <p className="text-muted text-center mb-4">Enter your details to get personalized recipe recommendations</p>
                    {error && <Alert variant="danger">{error}</Alert>}

                    {!isNewUser ? (
                        <Form onSubmit={handleUsernameSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label>Username *</Form.Label>
                                <Form.Control 
                                    type="text" 
                                    placeholder="Choose a unique username" 
                                    value={username} 
                                    onChange={(e) => setUsername(e.target.value)} 
                                    required 
                                />
                                <Form.Text className="text-muted">
                                    If you've used this app before, enter your previous username to load your profile
                                </Form.Text>
                            </Form.Group>
                            <Button variant="primary" type="submit" className="w-100" disabled={loading}>
                                 {loading ? 'Checking...' : 'Continue'}
                            </Button>
                        </Form>
                    ) : (
                        <Form onSubmit={handleRegistrationSubmit}>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Username *</Form.Label>
                                        <Form.Control type="text" value={username} disabled />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Name *</Form.Label>
                                        <Form.Control type="text" placeholder="Enter your full name" value={name} onChange={(e) => setName(e.target.value)} required />
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Age *</Form.Label>
                                        <Form.Control type="number" placeholder="Age" value={age} onChange={(e) => setAge(e.target.value)} required />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Gender</Form.Label>
                                        <Form.Select value={gender} onChange={(e) => setGender(e.target.value)}>
                                            <option value="male">Male</option>
                                            <option value="female">Female</option>
                                            <option value="other">Other</option>
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Height (cm) *</Form.Label>
                                        <Form.Control type="number" placeholder="Height in cm" value={height} onChange={(e) => setHeight(e.target.value)} required />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Weight (kg) *</Form.Label>
                                        <Form.Control type="number" placeholder="Weight in kg" value={weight} onChange={(e) => setWeight(e.target.value)} required />
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Form.Group className="mb-3">
                                <Form.Label>Activity Level</Form.Label>
                                <Form.Select value={activityLevel} onChange={(e) => setActivityLevel(e.target.value)}>
                                    <option value="1.2">Sedentary (little or no exercise)</option>
                                    <option value="1.375">Lightly active (1-3 days/week)</option>
                                    <option value="1.55">Moderately active (3-5 days/week)</option>
                                    <option value="1.725">Very active (6-7 days/week)</option>
                                    <option value="1.9">Extremely active (physical job)</option>
                                </Form.Select>
                            </Form.Group>
                            <Form.Group className="mb-4">
                                <Form.Label>Health Conditions</Form.Label>
                                <div>
                                    <Form.Check 
                                        type="checkbox" 
                                        label="Obesity (Weight management needed)" 
                                        checked={conditions.includes('obesity')}
                                        onChange={() => handleConditionChange('obesity')}
                                    />
                                    <Form.Check 
                                        type="checkbox" 
                                        label="Diabetes (Sugar and glycemic control)" 
                                        checked={conditions.includes('diabetes')}
                                        onChange={() => handleConditionChange('diabetes')}
                                    />
                                </div>
                            </Form.Group>
                             <Button variant="success" type="submit" className="w-100" disabled={loading}>
                                 {loading ? 'Registering...' : 'Register & Login'}
                             </Button>
                        </Form>
                    )}
                 </Card.Body>
             </Card>
         </Container>
     );
}

export default UserProfile;
