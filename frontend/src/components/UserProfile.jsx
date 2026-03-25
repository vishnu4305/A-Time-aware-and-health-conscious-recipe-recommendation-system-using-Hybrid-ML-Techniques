import React, { useState } from 'react';
import { Card, Form, Button, Alert, Row, Col } from 'react-bootstrap';
import axios from 'axios';
import { Form, Button, Card, Container, Row, Col, Alert } from 'react-bootstrap';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

function UserProfile({ onUserCreated }) {
  const [formData, setFormData] = useState({
    username: '',
    name: '',
    age: '',
    height: '',
    weight: '',
    gender: 'male',
    activity_level: '1.2',
    conditions: []
  });
    const [username, setUsername] = useState('');
    const [isNewUser, setIsNewUser] = useState(false);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
    // Full profile states
    const [name, setName] = useState('');
    const [age, setAge] = useState('');
    const [height, setHeight] = useState('');
    const [weight, setWeight] = useState('');
    const [gender, setGender] = useState('male');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
    // Step 1: Handle checking the username
    const handleUsernameSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

  const handleConditionChange = (condition) => {
    setFormData(prev => {
      const conditions = prev.conditions.includes(condition)
        ? prev.conditions.filter(c => c !== condition)
        : [...prev.conditions, condition];
      return { ...prev, conditions };
    });
  };
        try {
            const response = await fetch(`${API_BASE_URL}/user/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username })
            });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
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

    // Validation
    if (!formData.username || !formData.name || !formData.age || !formData.height || !formData.weight) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }
    // Step 2: Handle full registration
    const handleRegistrationSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

    try {
      // Check if user exists by username
      const checkResponse = await axios.get(`${API_URL}/user/by-username/${formData.username}`);
      
      if (checkResponse.data) {
        // User exists, update their profile with the new form data
        const updateResponse = await axios.put(`${API_URL}/user/update/${checkResponse.data.id}`, {
          name: formData.name,
          age: parseInt(formData.age),
          height: parseFloat(formData.height),
          weight: parseFloat(formData.weight),
          gender: formData.gender,
          activity_level: parseFloat(formData.activity_level),
          conditions: formData.conditions
        });
        onUserCreated(updateResponse.data.user);
        setLoading(false);
        return;
      }
    } catch (err) {
      // User doesn't exist, create new
    }
        const userData = { username, name, age: parseInt(age), height: parseFloat(height), weight: parseFloat(weight), gender };

    try {
      // Create new user
      const response = await axios.post(`${API_URL}/user/create`, {
        username: formData.username,
        name: formData.name,
        age: parseInt(formData.age),
        height: parseFloat(formData.height),
        weight: parseFloat(formData.weight),
        gender: formData.gender,
        activity_level: parseFloat(formData.activity_level),
        conditions: formData.conditions
      });
        try {
            const response = await fetch(`${API_BASE_URL}/user/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });

      onUserCreated(response.data.user);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create user profile');
    } finally {
      setLoading(false);
    }
  };
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
    <Row className="justify-content-center">
      <Col md={8} lg={6}>
        <Card className="shadow-sm">
          <Card.Header as="h4" className="text-white">
            👤 User Profile
          </Card.Header>
          <Card.Body>
            <p className="text-muted mb-4">
              Enter your details to get personalized recipe recommendations
            </p>
    return (
        <Container className="d-flex justify-content-center mt-5">
            <Card style={{ width: '600px' }}>
                <Card.Body>
                    <h2 className="text-center mb-4">Welcome!</h2>
                    {error && <Alert variant="danger">{error}</Alert>}

            {error && <Alert variant="danger">{error}</Alert>}

            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label>Username *</Form.Label>
                <Form.Control
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Choose a unique username"
                  required
                />
                <Form.Text className="text-muted">
                  If you've used this app before, enter your previous username to load your profile
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Name *</Form.Label>
                <Form.Control
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter your full name"
                  required
                />
              </Form.Group>

              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Age *</Form.Label>
                    <Form.Control
                      type="number"
                      name="age"
                      value={formData.age}
                      onChange={handleChange}
                      placeholder="Age"
                      min="1"
                      max="120"
                      required
                    />
                  </Form.Group>
                </Col>

                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Gender</Form.Label>
                    <Form.Select
                      name="gender"
                      value={formData.gender}
                      onChange={handleChange}
                    >
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>

              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Height (cm) *</Form.Label>
                    <Form.Control
                      type="number"
                      name="height"
                      value={formData.height}
                      onChange={handleChange}
                      placeholder="Height in cm"
                      min="50"
                      max="250"
                      required
                    />
                  </Form.Group>
                </Col>

                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Weight (kg) *</Form.Label>
                    <Form.Control
                      type="number"
                      name="weight"
                      value={formData.weight}
                      onChange={handleChange}
                      placeholder="Weight in kg"
                      min="20"
                      max="300"
                      required
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Form.Group className="mb-3">
                <Form.Label>Activity Level</Form.Label>
                <Form.Select
                  name="activity_level"
                  value={formData.activity_level}
                  onChange={handleChange}
                >
                  <option value="1.2">Sedentary (little or no exercise)</option>
                  <option value="1.375">Lightly active (1-3 days/week)</option>
                  <option value="1.55">Moderately active (3-5 days/week)</option>
                  <option value="1.725">Very active (6-7 days/week)</option>
                  <option value="1.9">Extremely active (physical job)</option>
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Health Conditions</Form.Label>
                <div>
                  <Form.Check
                    type="checkbox"
                    label="Obesity (Weight management needed)"
                    checked={formData.conditions.includes('obesity')}
                    onChange={() => handleConditionChange('obesity')}
                  />
                  <Form.Check
                    type="checkbox"
                    label="Diabetes (Sugar and glycemic control)"
                    checked={formData.conditions.includes('diabetes')}
                    onChange={() => handleConditionChange('diabetes')}
                  />
                </div>
              </Form.Group>

              <Button
                variant="primary"
                type="submit"
                className="w-100"
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Continue to Recommendations'}
              </Button>
            </Form>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
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
