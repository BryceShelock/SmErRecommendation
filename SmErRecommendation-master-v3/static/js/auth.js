// Authentication utility
const auth = {
  // Store user data after login
  setUser: function(userData) {
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('isLoggedIn', 'true');
  },
  
  // Get current user data
  getUser: function() {
    return JSON.parse(localStorage.getItem('user') || '{}');
  },
  
  // Check if user is logged in
  isLoggedIn: function() {
    return localStorage.getItem('isLoggedIn') === 'true';
  },
  
  // Log out user
  logout: function() {
    localStorage.removeItem('user');
    localStorage.setItem('isLoggedIn', 'false');
    window.location.href = '/login/';
  },
  
  // Check auth on protected pages
  checkAuth: function() {
    if (!this.isLoggedIn()) {
      window.location.href = '/login/';
      return false;
    }
    return true;
  }
}; 