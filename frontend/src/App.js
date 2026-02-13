import React, { useState } from 'react';
import { Container, Navbar, Nav } from 'react-bootstrap';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import UserProfile from './components/UserProfile';
import Dashboard from './components/Dashboard';
import ProfilePage from './components/ProfilePage';

function App() {
  const [currentUser, setCurrentUser] = useState(null);

  const handleUserCreated = (user) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    setCurrentUser(null);
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
        </Container>

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
    </Router>
  );
}

export default App;
