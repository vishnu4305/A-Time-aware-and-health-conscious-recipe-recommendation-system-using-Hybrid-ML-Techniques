import React from 'react';
import { Card, Badge } from 'react-bootstrap';

function RecipeCard({ recipe, onClick, showCalorieFit = false }) {
  const truncateText = (text, maxLength) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <Card className="h-100" style={{ cursor: 'pointer' }} onClick={onClick}>
      <Card.Body>
        <Card.Title>{truncateText(recipe.name, 50)}</Card.Title>
        
        {/* Calorie Fitness (for meal plans) */}
        {showCalorieFit && recipe.calorie_fitness !== undefined && (
          <div className="mb-2">
            <Badge 
              bg={recipe.calorie_fitness > 0.7 ? 'success' : 'warning'}
              className="me-1"
            >
              {(recipe.calorie_fitness * 100).toFixed(0)}% Calorie Match
            </Badge>
            {recipe.target_calories && (
              <small className="text-muted ms-1">
                (Target: {Math.round(recipe.target_calories)} kcal)
              </small>
            )}
          </div>
        )}
        
        {/* Nutrition Info */}
        <div className="mb-2">
          <Badge bg="success" className="me-1">
            {recipe.calories || 0} cal
          </Badge>
          <Badge bg="info" className="me-1">
            P: {recipe.protein || 0}g
          </Badge>
          <Badge bg="warning" text="dark" className="me-1">
            C: {recipe.carbs || 0}g
          </Badge>
          <Badge bg="danger" className="me-1">
            F: {recipe.fat || 0}g
          </Badge>
        </div>

        {/* Sugar & Sodium */}
        <div className="mb-2">
          <small className="text-muted">
            Sugar: {recipe.sugar || 0}g | Sodium: {recipe.sodium || 0}mg
            {recipe.gl && ` | GL: ${recipe.gl.toFixed(1)}`}
          </small>
        </div>

        {/* Scores */}
        <div className="mb-2">
          <small>
            <strong>Final Score:</strong> {recipe.final_score?.toFixed(2) || 'N/A'}
            <br />
            <strong>Taste:</strong> {recipe.preference_score?.toFixed(2) || 'N/A'} | 
            <strong> Health:</strong> {recipe.health_score?.toFixed(2) || 'N/A'}
          </small>
        </div>

        {/* Explanation */}
        {recipe.explanation && (
          <Card.Text className="text-muted" style={{ fontSize: '0.85em' }}>
            {truncateText(recipe.explanation, 100)}
          </Card.Text>
        )}

        <div className="text-center mt-2">
          <small className="text-primary">Click for details →</small>
        </div>
      </Card.Body>
    </Card>
  );
}

export default RecipeCard;
