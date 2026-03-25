import React, { useState } from 'react';
import { Button, Card, Container, Row, Col, Form, Spinner, Alert } from 'react-bootstrap';

const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

function Dashboard({ user }) {
  const [recommendations, setRecommendations] = useState([]);
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [gamma, setGamma] = useState(0.5);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user._id, gamma: parseFloat(gamma) }),
      });
      const data = await response.json();
      if (response.ok) {
        setRecommendations(data.recommendations);
        setMealPlan(null); // Clear meal plan when getting recommendations
      } else {
        setError(data.error || 'Failed to fetch recommendations.');
      }
    } catch (err) {
      setError('Could not connect to the server.');
    } finally {
      setLoading(false);
    }
  };

  const fetchMealPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/recommend/meal-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user._id, gamma: parseFloat(gamma) }),
      });
      const data = await response.json();
      if (response.ok) {
        setMealPlan(data);
        setRecommendations([]); // Clear recommendations when getting meal plan
      } else {
        setError(data.error || 'Failed to fetch meal plan.');
      }
    } catch (err) {
      setError('Could not connect to the server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <div className="slider-container card">
        <Card.Body>
          <h4 className="text-center mb-3">Personalize Your Results</h4>
          <Form.Group>
            <Form.Label>Taste vs. Health Preference</Form.Label>
            <div className="d-flex justify-content-between text-muted small">
              <span>More Taste (0.0)</span>
              <span>Balanced (0.5)</span>
              <span>More Health (1.0)</span>
            </div>
            <Form.Range 
              min="0" 
              max="1" 
              step="0.1" 
              value={gamma} 
              onChange={(e) => setGamma(e.target.value)} 
            />
          </Form.Group>
          <Row className="mt-3">
            <Col>
              <Button variant="primary" onClick={fetchRecommendations} className="w-100" disabled={loading}>
                Get Recipe Ideas
              </Button>
            </Col>
            <Col>
              <Button variant="secondary" onClick={fetchMealPlan} className="w-100" disabled={loading}>
                Generate Daily Meal Plan
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </div>
      {/* ... rendering logic ... */}
    </Container>
  );
}

export default Dashboard;
