import React, { useState, useEffect, useCallback } from 'react';
import { Card, Button, Alert, Row, Col, Badge, Form } from 'react-bootstrap';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ProfilePage({ user, onUserChange }) {
  const [userDetails, setUserDetails] = useState(user); // Start with user prop data
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState(user);
  const [updateSuccess, setUpdateSuccess] = useState('');

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

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditForm(prev => ({ ...prev, [name]: value }));
  };

  const handleConditionChange = (condition) => {
    setEditForm(prev => {
      const conditions = getConditionsArray(prev.conditions);
      const newConditions = conditions.includes(condition)
        ? conditions.filter(c => c !== condition)
        : [...conditions, condition];
      return { ...prev, conditions: newConditions };
    });
  };

  const handleUpdateSubmit = async () => {
    try {
      setLoading(true);
      setError('');
      setUpdateSuccess('');
      const userId = user.id || user._id;
      const response = await axios.put(`${API_URL}/user/update/${userId}`, {
        name: userDetails.name, // Name remains unchanged
        age: parseInt(editForm.age),
        height: parseFloat(editForm.height),
        weight: parseFloat(editForm.weight),
        gender: editForm.gender,
        activity_level: parseFloat(editForm.activity_level),
        conditions: getConditionsArray(editForm.conditions)
      });
      setUserDetails(response.data.user);
      setIsEditing(false);
      setUpdateSuccess('Profile updated successfully!');
      if (onUserChange) onUserChange(response.data.user);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

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
      {updateSuccess && <Alert variant="success">{updateSuccess}</Alert>}

      <Row>
        <Col md={8}>
          <Card className="mb-4">
            <Card.Header>
              <h4>Personal Information</h4>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <p className="mb-3"><strong>Name:</strong> {userDetails.name}</p>
                  <div className="mb-3">
                    <strong>Age:</strong> 
                    {isEditing ? <Form.Control type="number" name="age" value={editForm.age || ''} onChange={handleEditChange} size="sm" className="mt-1" /> : ` ${userDetails.age} years`}
                  </div>
                  <div className="mb-3">
                    <strong>Gender:</strong> 
                    {isEditing ? (
                      <Form.Select name="gender" value={editForm.gender || 'male'} onChange={handleEditChange} size="sm" className="mt-1">
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </Form.Select>
                    ) : ` ${userDetails.gender}`}
                  </div>
                </Col>
                <Col md={6}>
                  <div className="mb-3">
                    <strong>Height:</strong> 
                    {isEditing ? <Form.Control type="number" name="height" value={editForm.height || ''} onChange={handleEditChange} size="sm" className="mt-1" /> : ` ${userDetails.height} cm`}
                  </div>
                  <div className="mb-3">
                    <strong>Weight:</strong> 
                    {isEditing ? <Form.Control type="number" name="weight" value={editForm.weight || ''} onChange={handleEditChange} size="sm" className="mt-1" /> : ` ${userDetails.weight} kg`}
                  </div>
                  {!isEditing && <p><strong>BMI:</strong> {bmi} {bmiCategory && `(${bmiCategory})`}</p>}
                </Col>
              </Row>
            </Card.Body>
          </Card>

          <Card className="mb-4">
            <Card.Header>
              <h4>Health & Activity</h4>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <strong>Activity Level:</strong> 
                {isEditing ? (
                  <Form.Select name="activity_level" value={editForm.activity_level || '1.2'} onChange={handleEditChange} size="sm" className="mt-1">
                    <option value="1.2">Sedentary (little or no exercise)</option>
                    <option value="1.375">Lightly active (light exercise 1-3 days/week)</option>
                    <option value="1.55">Moderately active (moderate exercise 3-5 days/week)</option>
                    <option value="1.725">Very active (hard exercise 6-7 days/week)</option>
                    <option value="1.9">Extremely active (very hard exercise & physical job)</option>
                  </Form.Select>
                ) : ` ${getActivityLevelDescription(userDetails.activity_level)}`}
              </div>
              
              <div>
                <strong>Health Conditions:</strong>
                <div className="mt-2">
                  {isEditing ? (
                    <>
                      <Form.Check type="checkbox" label="Obesity (Weight management needed)" checked={getConditionsArray(editForm.conditions).includes('obesity')} onChange={() => handleConditionChange('obesity')} />
                      <Form.Check type="checkbox" label="Diabetes (Sugar and glycemic control)" checked={getConditionsArray(editForm.conditions).includes('diabetes')} onChange={() => handleConditionChange('diabetes')} />
                    </>
                  ) : (
                    conditionsArray && conditionsArray.length > 0 ? conditionsArray.map((condition, index) => (
                      <Badge key={index} bg="secondary" className="me-2 mb-1">{condition}</Badge>
                    )) : ' None'
                  )}
                </div>
              </div>
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
                {isEditing 
                  ? "Make changes to your profile and save."
                  : "Keep your profile up to date to get the best recommendations."}
              </p>
              {isEditing ? (
                <>
                  <Button variant="success" onClick={handleUpdateSubmit} className="w-100 mb-2" disabled={loading}>
                    {loading ? 'Saving...' : 'Save Changes'}
                  </Button>
                  <Button variant="outline-secondary" onClick={() => { setIsEditing(false); setEditForm(userDetails); }} className="w-100" disabled={loading}>
                    Cancel
                  </Button>
                </>
              ) : (
                <Button variant="outline-primary" onClick={() => { setEditForm(userDetails); setIsEditing(true); }} className="w-100">
                  Edit Profile
                </Button>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default ProfilePage;