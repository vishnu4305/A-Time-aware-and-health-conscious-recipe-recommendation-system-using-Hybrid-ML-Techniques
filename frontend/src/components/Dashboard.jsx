import React, { useState } from 'react';
import { Button, Card, Container, Row, Col, Form, Spinner, Alert } from 'react-bootstrap';

const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

function Dashboard({ user }) {
  const [recommendations, setRecommendations] = useState([]);
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [gamma, setGamma] = useState(0.5);

  // Safely get user ID
  const userId = user ? (user._id || user.id) : localStorage.getItem('user_id');

  const fetchRecommendations = async () => {
    if (!userId) {
      setError("User session lost. Please log in again.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, gamma: parseFloat(gamma) }),
      });
      const data = await response.json();
      if (response.ok) {
        setRecommendations(data.recommendations || []);
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
    if (!userId) {
      setError("User session lost. Please log in again.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/recommend/meal-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, gamma: parseFloat(gamma) }),
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
    <Container className="mt-4">
      <Card className="mb-4 shadow-sm border-0">
        <Card.Body>
          <h4 className="text-center mb-3">Personalize Your Results</h4>
          <Form.Group>
            <Form.Label className="fw-bold">Taste vs. Health Preference</Form.Label>
            <div className="d-flex justify-content-between text-muted small mb-1">
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
          <Row className="mt-4">
            <Col sm={6} className="mb-2 mb-sm-0">
              <Button variant="primary" onClick={fetchRecommendations} className="w-100 py-2 fw-bold" disabled={loading}>
                {loading && recommendations.length === 0 && !mealPlan ? 'Loading...' : 'Get Recipe Ideas'}
              </Button>
            </Col>
            <Col sm={6}>
              <Button variant="secondary" onClick={fetchMealPlan} className="w-100 py-2 fw-bold" disabled={loading}>
                Generate Daily Meal Plan
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Loading Spinner */}
      {loading && (
        <div className="text-center my-5 py-5">
          <Spinner animation="border" variant="primary" style={{ width: '3rem', height: '3rem' }} />
          <h5 className="mt-3 text-muted">🧠 AI is analyzing recipes... please wait.</h5>
        </div>
      )}

      {/* Error Message */}
      {error && <Alert variant="danger">{error}</Alert>}

      {/* Recommendations Grid */}
      {!loading && recommendations.length > 0 && (
        <div>
          <h3 className="mb-4">Your Top Recommendations</h3>
          <Row>
            {recommendations.map((recipe, index) => (
              <Col md={6} lg={4} key={index} className="mb-4">
                <Card className="h-100 shadow-sm border-primary">
                  <Card.Header className="bg-primary text-white fw-bold text-truncate" title={recipe.name}>
                    {recipe.name}
                  </Card.Header>
                  <Card.Body className="d-flex flex-column">
                    <p className="mb-1"><strong>⏱️ Time:</strong> {recipe.minutes} mins</p>
                    <p className="mb-1"><strong>🛒 Ingredients:</strong> {recipe.n_ingredients}</p>
                    <p className="mb-3"><strong>🔥 Calories:</strong> {recipe.calories} kcal</p>
                    <hr className="mt-auto mb-3" />
                    <div className="small text-muted">{recipe.explanation}</div>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}
    </Container>
  );
}

export default Dashboard;
