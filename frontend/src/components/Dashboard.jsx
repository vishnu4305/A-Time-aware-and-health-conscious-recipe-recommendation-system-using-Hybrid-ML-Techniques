import React, { useState } from 'react';
import { Card, Button, Row, Col, Alert, Form, Badge, ButtonGroup } from 'react-bootstrap';
import axios from 'axios';
import RecipeCard from './RecipeCard';
import RecipeDetail from './RecipeDetail';
import MealPlanView from './MealPlanView';

const API_BASE_URL = 'https://recipe-recommender-api-57hq.onrender.com';

function Dashboard({ user }) {
  const [gamma, setGamma] = useState(0.5);
  const [lambda, setLambda] = useState(2.5);
  const [recommendations, setRecommendations] = useState([]);
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [viewMode, setViewMode] = useState('normal'); // 'normal' or 'meal-plan'

  // Safely parse conditions whether they are an array or a JSON string
  const getConditionsList = () => {
    if (!user || !user.conditions) return [];
    if (Array.isArray(user.conditions)) return user.conditions;
    try { return JSON.parse(user.conditions); } catch (e) { return []; }
  };

  const getGammaLabel = () => {
    if (gamma === 0) return 'Pure Taste';
    if (gamma === 1) return 'Pure Health';
    return 'Balanced';
  };

  const handleGetRecommendations = async () => {
    setError('');
    setLoading(true);

    try {
      if (viewMode === 'meal-plan') {
        // Get meal plan
        const response = await axios.post(`${API_BASE_URL}/recommend/meal-plan`, {
          user_id: user._id || user.id,
          gamma: gamma,
          lambda_decay: lambda,
          recipes_per_meal: 3
        });

        setMealPlan(response.data);
        setRecommendations([]);
      } else {
        // Get normal recommendations
        const response = await axios.post(`${API_BASE_URL}/recommend`, {
          user_id: user._id || user.id,
          gamma: gamma,
          lambda_decay: lambda,
          top_n: 12
        });

        setRecommendations(response.data.recommendations || []);
        setMealPlan(null);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleRecipeClick = (recipe) => {
    setSelectedRecipe(recipe);
  };

  const handleCloseDetail = () => {
    setSelectedRecipe(null);
  };

  const handleRatingSubmitted = () => {
    // Optionally refresh recommendations after rating
    setSelectedRecipe(null);
  };

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
    setRecommendations([]);
    setMealPlan(null);
    setError('');
  };

  if (selectedRecipe) {
    return (
      <RecipeDetail
        recipe={selectedRecipe}
        user={user}
        onClose={handleCloseDetail}
        onRatingSubmitted={handleRatingSubmitted}
      />
    );
  }

  return (
    <div>
      {/* User Info Card */}
      <Card className="mb-4 shadow-sm border-0">
        <Card.Body className="py-3">
          <Row className="align-items-center">
            <Col md={8}>
              <h5 className="mb-2">👤 {user.name}'s Profile</h5>
              <p className="mb-1 text-muted">
                <strong>Age:</strong> {user.age} | <strong>Height:</strong> {user.height} cm | <strong>Weight:</strong> {user.weight} kg
              </p>
              {getConditionsList().length > 0 && (
                <p className="mb-0">
                  <strong>Health Conditions:</strong>{' '}
                  {getConditionsList().map((condition, idx) => (
                    <Badge key={idx} bg="warning" text="dark" className="me-1">
                      {condition}
                    </Badge>
                  ))}
                </p>
              )}
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Control Panel */}
      <Card className="mb-4 shadow-sm border-0">
        <Card.Header className="text-white">
          ⚙️ Recommendation Preferences
        </Card.Header>
        <Card.Body>
          {/* View Mode Toggle */}
          <div className="mb-4 text-center">
            <ButtonGroup>
              <Button
                variant={viewMode === 'normal' ? 'primary' : 'outline-primary'}
                onClick={() => handleViewModeChange('normal')}
              >
                📋 Regular Recommendations
              </Button>
              <Button
                variant={viewMode === 'meal-plan' ? 'primary' : 'outline-primary'}
                onClick={() => handleViewModeChange('meal-plan')}
              >
                🍽️ Daily Meal Plan
              </Button>
            </ButtonGroup>
            <div className="mt-2">
              <small className="text-muted">
                {viewMode === 'meal-plan' 
                  ? 'Get organized meal recommendations for breakfast, lunch, snacks, and dinner'
                  : 'Get a list of personalized recipe recommendations'
                }
              </small>
            </div>
          </div>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>
                  <strong>Taste vs Health (γ): </strong>
                  <Badge bg="info">{getGammaLabel()} ({gamma})</Badge>
                </Form.Label>
                <Form.Range
                  min="0"
                  max="1"
                  step="0.1"
                  value={gamma}
                  onChange={(e) => setGamma(parseFloat(e.target.value))}
                />
                <Form.Text>
                  <strong>0 = Pure Taste</strong> (ignore health) | 
                  <strong> 0.5 = Balanced</strong> | 
                  <strong> 1 = Pure Health</strong> (ignore taste)
                </Form.Text>
              </Form.Group>
            </Col>

            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>
                  <strong>Time Sensitivity (λ): </strong>
                  <Badge bg="secondary">{lambda}</Badge>
                </Form.Label>
                <Form.Range
                  min="0.5"
                  max="4"
                  step="0.1"
                  value={lambda}
                  onChange={(e) => setLambda(parseFloat(e.target.value))}
                />
                <Form.Text>
                  Higher values = more focus on recent preferences
                </Form.Text>
              </Form.Group>
            </Col>
          </Row>

          <Button
            variant="primary"
            size="lg"
            className="w-100"
            onClick={handleGetRecommendations}
            disabled={loading}
          >
            {loading 
              ? 'Loading...' 
              : viewMode === 'meal-plan'
                ? '🍽️ Get Daily Meal Plan'
                : '🔍 Get Personalized Recommendations'
            }
          </Button>
        </Card.Body>
      </Card>

      {/* Error Message */}
      {error && <Alert variant="danger">{error}</Alert>}

      {/* Meal Plan View */}
      {viewMode === 'meal-plan' && mealPlan && (
        <MealPlanView 
          mealPlan={mealPlan} 
          onRate={setSelectedRecipe}
        />
      )}

      {/* Normal Recommendations View */}
      {viewMode === 'normal' && recommendations && recommendations.length > 0 && (
        <div>
          <h4 className="mb-3" style={{color: '#0891b2', fontWeight: '700'}}>
            🍴 Your Recommendations ({recommendations.length})
          </h4>
          <div className="recommendation-grid">
            {recommendations.map((recipe, idx) => (
              <RecipeCard
                key={idx}
                recipe={recipe}
                onClick={() => handleRecipeClick(recipe)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && (!recommendations || recommendations.length === 0) && !mealPlan && !error && (
        <Card className="text-center">
          <Card.Body className="py-5">
            <h5 className="text-muted">No recommendations yet</h5>
            <p className="text-muted">
              {viewMode === 'meal-plan'
                ? 'Click the button above to get your personalized daily meal plan'
                : 'Adjust the sliders and click the button above to get personalized recommendations'
              }
            </p>
          </Card.Body>
        </Card>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-3 text-muted">Analyzing your preferences...</p>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
