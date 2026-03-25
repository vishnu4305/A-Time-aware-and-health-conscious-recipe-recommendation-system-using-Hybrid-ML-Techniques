import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { Navbar, Container, Button } from 'react-bootstrap';
import UserProfile from './components/UserProfile';
import Dashboard from './components/Dashboard';
import ProfilePage from './components/ProfilePage';

function App() {
  // Initialize state from localStorage to keep the user logged in on refresh
  const [currentUser, setCurrentUser] = useState(() => {
    const savedUser = localStorage.getItem('user_data');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  // This effect syncs localStorage whenever the currentUser state changes
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('user_data', JSON.stringify(currentUser));
      localStorage.setItem('user_id', currentUser._id || currentUser.id);
    } else {
      localStorage.removeItem('user_data');
      localStorage.removeItem('user_id');
    }
  }, [currentUser]);

  const handleLogout = () => {
    setCurrentUser(null); // This will trigger the useEffect to clear localStorage
  };

  return (
    <Router>
      <Navbar bg="primary" variant="dark" expand="lg" className="shadow-sm">
        <Container>
          <Navbar.Brand as={Link} to={currentUser ? "/dashboard" : "/"} className="fw-bold">🍽️ Smart Recipes</Navbar.Brand>
          {currentUser && (
            <div className="ms-auto">
              <Link to="/profile" className="btn btn-secondary me-2 text-white" style={{ textDecoration: 'none' }}>My Profile</Link>
              <Button variant="danger" onClick={handleLogout}>Logout</Button>
            </div>
          )}
        </Container>
      </Navbar>

      <main className="py-4">
        <Routes>
          <Route path="/" element={
            currentUser ? <Navigate to="/dashboard" replace /> : <UserProfile onUserCreated={setCurrentUser} />
          } />
          <Route path="/dashboard" element={
            currentUser ? <Dashboard user={currentUser} /> : <Navigate to="/" replace />
          } />
          <Route path="/profile" element={
            currentUser ? <ProfilePage user={currentUser} onUserChange={setCurrentUser} /> : <Navigate to="/" replace />
          } />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
