import React, { useState, useEffect, useCallback } from 'react';
import { Card, Button, Alert, Row, Col, Badge } from 'react-bootstrap';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ProfilePage({ user, onUserChange }) {
  const [userDetails, setUserDetails] = useState(user); // Start with user prop data
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchUserDetails = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/user/${user.id}`);
      setUserDetails(response.data);
      setError('');
    } catch (err) {
      // If API fails, keep using the user prop data
      setUserDetails(user);
      setError('');
      console.error('Error fetching user details:', err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchUserDetails();
  }, [fetchUserDetails]);

  const getConditionsArray = (conditions) => {
    if (!conditions) return [];
    if (Array.isArray(conditions)) return conditions;
    if (typeof conditions === 'string') {
      try {
        return JSON.parse(conditions);
      } catch (e) {
        return [];
      }
    }
    return [];
  };

  const calculateBMI = (weight, height) => {
    if (!weight || !height) return null;
    const heightInMeters = height / 100;
    return (weight / (heightInMeters * heightInMeters)).toFixed(1);
  };

  const getBMICategory = (bmi) => {
    if (!bmi) return '';
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  };

  const getActivityLevelDescription = (level) => {
    const descriptions = {
      '1.2': 'Sedentary (little or no exercise)',
      '1.375': 'Lightly active (light exercise 1-3 days/week)',
      '1.55': 'Moderately active (moderate exercise 3-5 days/week)',
      '1.725': 'Very active (hard exercise 6-7 days/week)',
      '1.9': 'Extremely active (very hard exercise & physical job)'
    };
    return descriptions[level] || level;
  };

  const conditionsArray = getConditionsArray(userDetails.conditions);

  if (loading && !userDetails) {
    return (
      <div className="text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error && !userDetails) {
    return <Alert variant="danger">{error}</Alert>;
  }

  if (!userDetails) {
    return <Alert variant="warning">User profile not found</Alert>;
  }

  const bmi = calculateBMI(userDetails.weight, userDetails.height);
  const bmiCategory = getBMICategory(bmi);

  return (
    <div>
      <h2 className="mb-4">User Profile</h2>

      <Row>
        <Col md={8}>
          <Card className="mb-4">
            <Card.Header>
              <h4>Personal Information</h4>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <p><strong>Name:</strong> {userDetails.name}</p>
                  <p><strong>Age:</strong> {userDetails.age} years</p>
                  <p><strong>Gender:</strong> {userDetails.gender}</p>
                </Col>
                <Col md={6}>
                  <p><strong>Height:</strong> {userDetails.height} cm</p>
                  <p><strong>Weight:</strong> {userDetails.weight} kg</p>
                  <p><strong>BMI:</strong> {bmi} {bmiCategory && `(${bmiCategory})`}</p>
                </Col>
              </Row>
            </Card.Body>
          </Card>

          <Card className="mb-4">
            <Card.Header>
              <h4>Health & Activity</h4>
            </Card.Header>
            <Card.Body>
              <p><strong>Activity Level:</strong> {getActivityLevelDescription(userDetails.activity_level)}</p>
              {conditionsArray && conditionsArray.length > 0 && (
                <div>
                  <strong>Health Conditions:</strong>
                  <div className="mt-2">
                    {conditionsArray.map((condition, index) => (
                      <Badge key={index} bg="secondary" className="me-2 mb-1">
                        {condition}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={4}>
          <Card>
            <Card.Header>
              <h4>Actions</h4>
            </Card.Header>
            <Card.Body>
              <p className="text-muted small">
                To update your profile information, you'll need to create a new user profile.
              </p>
              <Button
                variant="outline-primary"
                onClick={onUserChange}
                className="w-100"
              >
                Update Profile
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default ProfilePage;