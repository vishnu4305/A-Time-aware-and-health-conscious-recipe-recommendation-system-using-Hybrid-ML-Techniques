import React, { useState } from 'react';
import { Card, Form, Button, Alert, Row, Col } from 'react-bootstrap';
import { Container } from 'react-bootstrap';

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
                                 />
                             </Form.Group>
                             <Button variant="primary" type="submit" className="w-100" disabled={loading}>
                                 {loading ? 'Checking...' : 'Continue'}
                             </Button>
                         </Form>
                     ) : (
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
