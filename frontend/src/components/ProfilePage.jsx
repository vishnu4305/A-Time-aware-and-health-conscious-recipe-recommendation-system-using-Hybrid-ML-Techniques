import React, { useState, useEffect } from 'react';
import { Form, Button, Card, Container, Row, Col, Alert } from 'react-bootstrap';

const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

function ProfilePage({ user, onUserChange }) {
    const [formData, setFormData] = useState({ ...user });
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [loading, setLoading] = useState(false);

    // When the user prop changes (e.g., after login), update the form data
    useEffect(() => {
        setFormData({ ...user });
    }, [user]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({ ...prevState, [name]: value }));
    };

    const handleConditionChange = (condition) => {
        setFormData(prev => {
            const currentConditions = prev.conditions || [];
            return {
                ...prev,
                conditions: currentConditions.includes(condition) 
                    ? currentConditions.filter(c => c !== condition)
                    : [...currentConditions, condition]
            };
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setLoading(true);

        const userId = user._id || user.id;

        try {
            const response = await fetch(`${API_BASE_URL}/user/update/${userId}`, {
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
                onUserChange(data.user); // Update the user in App.js state, which syncs localStorage
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
                         <Row>
                             <Col md={6}>
                                 <Form.Group className="mb-3">
                                     <Form.Label>Age</Form.Label>
                                     <Form.Control type="number" name="age" value={formData.age || ''} onChange={handleChange} required />
                                 </Form.Group>
                             </Col>
                             <Col md={6}>
                                 <Form.Group className="mb-3">
                                     <Form.Label>Gender</Form.Label>
                                     <Form.Select name="gender" value={formData.gender || 'male'} onChange={handleChange}>
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
                                     <Form.Control type="number" name="height" value={formData.height || ''} onChange={handleChange} required />
                                 </Form.Group>
                             </Col>
                             <Col md={6}>
                                 <Form.Group className="mb-3">
                                     <Form.Label>Weight (kg)</Form.Label>
                                     <Form.Control type="number" name="weight" value={formData.weight || ''} onChange={handleChange} required />
                                 </Form.Group>
                             </Col>
                         </Row>
                         <Form.Group className="mb-3">
                             <Form.Label>Activity Level</Form.Label>
                             <Form.Select name="activity_level" value={formData.activity_level || '1.2'} onChange={handleChange}>
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
                                     checked={(formData.conditions || []).includes('obesity')}
                                     onChange={() => handleConditionChange('obesity')}
                                 />
                                 <Form.Check 
                                     type="checkbox" 
                                     label="Diabetes (Sugar and glycemic control)" 
                                     checked={(formData.conditions || []).includes('diabetes')}
                                     onChange={() => handleConditionChange('diabetes')}
                                 />
                             </div>
                         </Form.Group>
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
