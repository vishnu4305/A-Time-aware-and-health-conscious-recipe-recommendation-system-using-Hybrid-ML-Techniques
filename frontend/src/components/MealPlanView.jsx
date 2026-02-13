import React from 'react';
import RecipeCard from './RecipeCard';

const MealPlanView = ({ mealPlan, onRate }) => {
  if (!mealPlan || !mealPlan.meal_plan) {
    return (
      <div className="alert alert-info">
        <h5>No meal plan available</h5>
        <p>Click "Get Meal Plan" to generate personalized meal recommendations.</p>
      </div>
    );
  }

  const { meal_plan, daily_calories, calorie_distribution } = mealPlan;

  const mealSections = [
    { key: 'breakfast', title: 'Breakfast', icon: '🌅', color: 'warning' },
    { key: 'lunch', title: 'Lunch', icon: '☀️', color: 'success' },
    { key: 'snacks', title: 'Snacks', icon: '🍎', color: 'info' },
    { key: 'dinner', title: 'Dinner', icon: '🌙', color: 'primary' }
  ];

  return (
    <div className="meal-plan-view">
      {/* Header with daily summary */}
      <div className="card mb-4 shadow-sm border-0">
        <div className="card-body py-4">
          <h4 className="card-title mb-4" style={{color: '#0891b2', fontWeight: '700'}}>
            📅 Your Daily Meal Plan
          </h4>
          <div className="row text-center">
            <div className="col-md-3">
              <h6 className="text-muted mb-2">Total Daily Calories</h6>
              <h3 style={{color: '#0891b2', fontWeight: '700'}}>{Math.round(daily_calories)}</h3>
              <small className="text-muted">kcal/day</small>
            </div>
            <div className="col-md-9">
              <h6 className="text-muted mb-3">Calorie Distribution</h6>
              <div className="d-flex justify-content-around">
                {mealSections.map(({ key, title, icon }) => (
                  <div key={key}>
                    <span className="me-1" style={{fontSize: '1.5rem'}}>{icon}</span>
                    <br />
                    <strong>{title}</strong>
                    <br />
                    <span className="badge" style={{backgroundColor: '#059669', fontSize: '0.9rem', padding: '0.4rem 0.8rem', marginTop: '0.25rem'}}>
                      {Math.round(calorie_distribution[key])} kcal
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Meal sections */}
      {mealSections.map(({ key, title, icon, color }) => {
        const mealData = meal_plan[key];
        const hasRecipes = mealData && mealData.recipes && mealData.recipes.length > 0;

        return (
          <div key={key} className="mb-4">
            <div className={`card border-${color} shadow-sm`}>
              <div className={`card-header bg-${color} text-white`}>
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">
                    <span className="me-2">{icon}</span>
                    {title}
                  </h5>
                  {mealData && (
                    <span className="badge bg-light text-dark">
                      Target: {Math.round(mealData.target_calories)} kcal
                    </span>
                  )}
                </div>
              </div>
              <div className="card-body">
                {!hasRecipes ? (
                  <div className="alert alert-light mb-0">
                    <p className="mb-0">
                      No suitable recipes found for this meal type. Try adjusting your preferences or rate more recipes to improve recommendations.
                    </p>
                  </div>
                ) : (
                  <div className="row g-3">
                    {mealData.recipes.map((recipe, index) => (
                      <div key={recipe.id || index} className="col-md-4">
                        <RecipeCard 
                          recipe={recipe} 
                          onClick={() => onRate(recipe)}
                          showCalorieFit={true}
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}

      {/* Footer note */}
      <div className="alert alert-info mt-4">
        <h6>💡 Tips for better meal plans:</h6>
        <ul className="mb-0">
          <li>Rate recipes you've tried to improve personalization</li>
          <li>Adjust the <strong>γ (gamma)</strong> slider to balance taste vs health</li>
          <li>Adjust the <strong>λ (lambda)</strong> slider to emphasize recent preferences</li>
          <li>Recipes are selected based on your calorie needs and health conditions</li>
        </ul>
      </div>
    </div>
  );
};

export default MealPlanView;
