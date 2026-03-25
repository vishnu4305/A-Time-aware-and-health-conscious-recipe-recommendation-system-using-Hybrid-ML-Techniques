import React, { useState, useEffect } from 'react';
import { Form, Button, Card, Container, Row, Col, Alert } from 'react-bootstrap';

const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

function ProfilePage({ user, onUserChange }) {
    const [formData, setFormData] = useState({ ...user });
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setFormData({ ...user });
    }, [user]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({ ...prevState, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/user/update/${user._id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...formData,
                    age: parseInt(formData.age),
                    height: parseFloat(formData.height),
                    weight: parseFloat(formData.weight)
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess("Profile updated successfully!");
                onUserChange(data.user); // Update the user in App.js state
            } else {
                setError(data.error || 'Failed to update profile.');
            }
        } catch (err) {
            setError('Could not connect to the server.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container className="d-flex justify-content-center mt-5">
            <Card style={{ width: '600px' }}>
                <Card.Body>
                    <h2 className="text-center mb-4">Update Your Profile</h2>
                    {error && <Alert variant="danger">{error}</Alert>}
                    {success && <Alert variant="success">{success}</Alert>}
                    <Form onSubmit={handleSubmit}>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Username</Form.Label>
                                    <Form.Control type="text" name="username" value={formData.username || ''} disabled />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Full Name</Form.Label>
                                    <Form.Control type="text" name="name" value={formData.name || ''} onChange={handleChange} required />
                                </Form.Group>
                            </Col>
                        </Row>
                        {/* ... other form fields for age, height, weight, etc. ... */}
                        <Button variant="primary" type="submit" className="w-100" disabled={loading}>
                            {loading ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </Form>
                </Card.Body>
            </Card>
        </Container>
    );
}

export default ProfilePage;
