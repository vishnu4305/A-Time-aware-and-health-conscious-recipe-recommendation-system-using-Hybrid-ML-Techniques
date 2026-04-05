import React, { useState } from 'react';
import { Card, Button, Badge, Alert, Row, Col } from 'react-bootstrap';
import axios from 'axios';

const RENDER_URL = process.env.REACT_APP_API_URL || 'https://recipe-recommender-api-57hq.onrender.com';
const LOCAL_URL = 'http://localhost:5000';
let workingUrl = RENDER_URL;

// Helper to automatically fallback to localhost if Render is asleep or fails
const safeAxiosPost = async (endpoint, payload) => {
  try {
    return await axios.post(`${workingUrl}${endpoint}`, payload);
  } catch (err) {
    const isNetworkError = !err.response || err.code === 'ERR_NETWORK';
    const isServerError = err.response && err.response.status >= 500;
    
    if ((isNetworkError || isServerError) && workingUrl !== LOCAL_URL) {
      console.warn(`Cloud backend offline. Falling back to local server at ${LOCAL_URL}...`);
      workingUrl = LOCAL_URL;
      return await axios.post(`${workingUrl}${endpoint}`, payload);
    }
    throw err;
  }
};

function RecipeDetail({ recipe, user, onClose, onRatingSubmitted }) {
  const [rating, setRating] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleRatingSubmit = async () => {
    if (rating === 0) {
      setError('Please select a rating');
      return;
    }

    setError('');
    setSubmitting(true);

    try {
      await safeAxiosPost('/rate', {
        user_id: user.id,
        recipe_id: recipe.id,
        rating: rating
      });

      setMessage('Rating submitted successfully!');
      setTimeout(() => {
        onRatingSubmitted();
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit rating');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <Button variant="secondary" onClick={onClose} className="mb-3">
        ← Back to Recommendations
      </Button>

      <Card>
        <Card.Header as="h3">
          {recipe.name}
        </Card.Header>
        <Card.Body>
          {/* Nutrition Summary */}
          <Card className="mb-3 bg-light">
            <Card.Body>
              <h5>Nutritional Information</h5>
              <Row>
                <Col md={3}>
                  <strong>Calories:</strong> {recipe.calories || 0} kcal
                </Col>
                <Col md={3}>
                  <strong>Protein:</strong> {recipe.protein || 0}g
                </Col>
                <Col md={3}>
                  <strong>Carbs:</strong> {recipe.carbs || 0}g
                </Col>
                <Col md={3}>
                  <strong>Fat:</strong> {recipe.fat || 0}g
                </Col>
              </Row>
              <Row className="mt-2">
                <Col md={3}>
                  <strong>Sugar:</strong> {recipe.sugar || 0}g
                </Col>
                <Col md={3}>
                  <strong>Sodium:</strong> {recipe.sodium || 0}mg
                </Col>
                <Col md={3}>
                  <strong>Glycemic Load:</strong> {recipe.gl?.toFixed(1) || 'N/A'}
                </Col>
              </Row>
            </Card.Body>
          </Card>

          {/* Recommendation Scores */}
          <Card className="mb-3">
            <Card.Body>
              <h5>Why This Recipe?</h5>
              <div className="mb-2">
                <Badge bg="primary" className="me-2">
                  Final Score: {recipe.final_score?.toFixed(2) || 'N/A'}
                </Badge>
                <Badge bg="info" className="me-2">
                  Taste Score: {recipe.preference_score?.toFixed(2) || 'N/A'}
                </Badge>
                <Badge bg="success">
                  Health Score: {recipe.health_score?.toFixed(2) || 'N/A'}
                </Badge>
              </div>
              {recipe.explanation && (
                <p className="text-muted mb-0">{recipe.explanation}</p>
              )}
            </Card.Body>
          </Card>

          {/* Ingredients */}
          <Card className="mb-3">
            <Card.Body>
              <h5>Ingredients</h5>
              <p style={{ whiteSpace: 'pre-wrap' }}>
                {recipe.ingredients || 'No ingredients listed'}
              </p>
            </Card.Body>
          </Card>

          {/* Steps */}
          {recipe.steps && recipe.steps.trim() !== '' && (
            <Card className="mb-3">
              <Card.Body>
                <h5>Instructions</h5>
                <p style={{ whiteSpace: 'pre-wrap' }}>
                  {recipe.steps}
                </p>
              </Card.Body>
            </Card>
          )}

          {/* Rating Section */}
          <Card className="mb-3">
            <Card.Body>
              <h5>Rate This Recipe</h5>
              <p className="text-muted">
                Your rating helps improve future recommendations
              </p>

              {message && <Alert variant="success">{message}</Alert>}
              {error && <Alert variant="danger">{error}</Alert>}

              <div className="mb-3">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Button
                    key={star}
                    variant={rating >= star ? 'warning' : 'outline-warning'}
                    size="lg"
                    className="me-2"
                    onClick={() => setRating(star)}
                    disabled={submitting}
                  >
                    ⭐
                  </Button>
                ))}
              </div>

              <Button
                variant="primary"
                onClick={handleRatingSubmit}
                disabled={submitting || rating === 0}
              >
                {submitting ? 'Submitting...' : 'Submit Rating'}
              </Button>
            </Card.Body>
          </Card>
        </Card.Body>
      </Card>
    </div>
  );
}

export default RecipeDetail;
