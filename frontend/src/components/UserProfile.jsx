import React, { useState } from 'react';
import { Form, Button, Card, Container, Row, Col, Alert } from 'react-bootstrap';

const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

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

    // Step 1: Handle checking the username
    const handleUsernameSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/user/login`, {
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

        const userData = { username, name, age: parseInt(age), height: parseFloat(height), weight: parseFloat(weight), gender };

        try {
            const response = await fetch(`${API_BASE_URL}/user/create`, {
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
                    <h2 className="text-center mb-4">Welcome!</h2>
                    {error && <Alert variant="danger">{error}</Alert>}

                    {!isNewUser ? (
                        <Form onSubmit={handleUsernameSubmit}>
                            <Form.Group className="mb-3">
                                <Form.Label>Enter Your Username</Form.Label>
                                <Form.Control 
                                    type="text" 
                                    placeholder="e.g., vishnu123" 
                                    value={username} 
                                    onChange={(e) => setUsername(e.target.value)} 
                                    required 
                                />
                            </Form.Group>
                            <Button variant="primary" type="submit" className="w-100" disabled={loading}>
                                {loading ? 'Checking...' : 'Continue'}
                            </Button>
                        </Form>
                    ) : (
                        <Form onSubmit={handleRegistrationSubmit}>
                            <h5 className="text-center mb-3">Complete Your Profile</h5>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Username</Form.Label>
                                        <Form.Control type="text" value={username} disabled />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Full Name</Form.Label>
                                        <Form.Control type="text" value={name} onChange={(e) => setName(e.target.value)} required />
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Age</Form.Label>
                                        <Form.Control type="number" value={age} onChange={(e) => setAge(e.target.value)} required />
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
                                        <Form.Label>Height (cm)</Form.Label>
                                        <Form.Control type="number" value={height} onChange={(e) => setHeight(e.target.value)} required />
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Weight (kg)</Form.Label>
                                        <Form.Control type="number" value={weight} onChange={(e) => setWeight(e.target.value)} required />
                                    </Form.Group>
                                </Col>
                            </Row>
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
