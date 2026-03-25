import React, { useState } from 'react';
import { Container, Navbar, Nav } from 'react-bootstrap';
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { Navbar, Container, Button } from 'react-bootstrap';
import UserProfile from './components/UserProfile';
import Dashboard from './components/Dashboard';
import ProfilePage from './components/ProfilePage';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  // Initialize state from localStorage to keep the user logged in on refresh
  const [currentUser, setCurrentUser] = useState(() => {
    const savedUser = localStorage.getItem('user_data');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const handleUserCreated = (user) => {
    setCurrentUser(user);
  };
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
    setCurrentUser(null);
    setCurrentUser(null); // This will trigger the useEffect to clear localStorage
  };

  return (
    <Router>
      <div className="App">
        {/* Navigation Bar */}
        <Navbar variant="dark" expand="lg" className="navbar">
          <Container>
            <Navbar.Brand href="#home" style={{ fontSize: '1.5rem', fontWeight: '700' }}>
              🍽️ Health and Time-Aware Recipe Recommender
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="ms-auto">
                {currentUser && (
                  <>
                    <Nav.Link as={Link} to="/dashboard" style={{ color: 'white', opacity: 0.9 }}>
                      Dashboard
                    </Nav.Link>
                    <Nav.Link as={Link} to="/profile" style={{ color: 'white', opacity: 0.9 }}>
                      Profile
                    </Nav.Link>
                    <Nav.Link disabled style={{ color: 'white', opacity: 0.9 }}>
                      Welcome, {currentUser.name}!
                    </Nav.Link>
                    <Nav.Link onClick={handleLogout} style={{ fontWeight: '600' }}>
                      Change User
                    </Nav.Link>
                  </>
                )}
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        {/* Main Content */}
        <Container className="mt-4">
          <Routes>
            <Route 
              path="/" 
              element={
                currentUser ? 
                  <Navigate to="/dashboard" replace /> : 
                  <UserProfile onUserCreated={handleUserCreated} />
              } 
            />
            <Route 
              path="/dashboard" 
              element={
                currentUser ? 
                  <Dashboard user={currentUser} /> : 
                  <Navigate to="/" replace />
              } 
            />
            <Route 
              path="/profile" 
              element={
                currentUser ? 
                  <ProfilePage user={currentUser} onUserChange={handleLogout} /> : 
                  <Navigate to="/" replace />
              } 
            />
          </Routes>
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

        {/* Footer */}
        <footer className="text-center text-muted mt-5 mb-3">
          <Container>
            <p>
              Health and Time-Aware Recipe Recommendation System
              <br />
              <small>Balancing taste preferences with health requirements using ML</small>
            </p>
          </Container>
        </footer>
      </div>
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
