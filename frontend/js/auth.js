/**
 * AcadGuard Auth Management & Session State
 */
const Auth = {
  getUser() {
    try {
      const stored = localStorage.getItem(CONFIG.USER_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch (_) {
      return null;
    }
  },

  isLoggedIn() {
    return !!localStorage.getItem(CONFIG.TOKEN_KEY) && !!this.getUser();
  },

  getRole() {
    const user = this.getUser();
    return user ? user.role : null;
  },

  async login(email, password) {
    try {
      const data = await API.post('/auth/login', { email, password });
      localStorage.setItem(CONFIG.TOKEN_KEY, data.access_token);
      localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(data.user));
      Toast.success('Login Successful', `Welcome back, ${data.user.full_name}!`);
      return data.user;
    } catch (err) {
      Toast.error('Login Failed', err.message);
      throw err;
    }
  },

  async register(formData) {
    try {
      const user = await API.post('/auth/register', formData);
      Toast.success('Account Created', 'Registration completed successfully. You can now login.');
      return user;
    } catch (err) {
      Toast.error('Registration Failed', err.message);
      throw err;
    }
  },

  logout() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.USER_KEY);
    Toast.info('Logged Out', 'You have been signed out.');
    setTimeout(() => {
      window.location.href = '/login';
    }, 500);
  },

  requireAuth(allowedRoles = []) {
    if (!this.isLoggedIn()) {
      window.location.href = '/login';
      return false;
    }
    const role = this.getRole();
    if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
      Toast.error('Access Denied', `Role '${role}' cannot access this section.`);
      setTimeout(() => {
        window.location.href = '/app';
      }, 1000);
      return false;
    }
    return true;
  }
};
